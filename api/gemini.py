import os
import requests
import threading
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PROMPT = os.getenv("PROMPT")  # Fetching the prompt from .env

# In-memory chat history storage
chat_history = {}

# Temporary response storage (for fetching later)
pending_responses = {}

def generate_response(user_id, message):
    """Fetch response from Gemini API asynchronously and store it in pending_responses."""
    try:
        history = chat_history.get(user_id, [])

        contents = [{"role": "user", "parts": [{"text": PROMPT}]}]  
        for entry in history:
            contents.append({"role": entry["role"], "parts": [{"text": entry["text"]}]})
        contents.append({"role": "user", "parts": [{"text": message}]})

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": contents}

        response = requests.post(url, json=payload)
        if response.status_code != 200:
            pending_responses[user_id] = "Error: Unable to fetch response at the moment."
            return

        data = response.json()
        if "candidates" in data and data["candidates"]:
            reply = data["candidates"][0]["content"]["parts"][0]["text"]

            chat_history[user_id] = history + [
                {"role": "user", "parts": [{"text": message}]},
                {"role": "model", "parts": [{"text": reply}]},
            ]

            pending_responses[user_id] = reply  # Store final response
        else:
            pending_responses[user_id] = "Error: Unable to fetch response at the moment."
    except Exception:
        pending_responses[user_id] = "Error: Unable to fetch response at the moment."

def process_chat_request(user_id, message):
    """Starts a separate thread to process chat response asynchronously."""
    thread = threading.Thread(target=generate_response, args=(user_id, message))
    thread.start()

# 🔹 GET request: Initiate conversation
@app.route("/pythonbotz", methods=["GET"])
def chat():
    user_id = request.args.get("user_id")
    message = request.args.get("msg")
    if not message or not user_id:
        return jsonify({"error": "user_id and msg parameters are required"}), 400

    process_chat_request(user_id, message)

    return jsonify({"reply": "Fetching response...", "Owner": "@PythonBotz"})

# 🔹 Polling endpoint: Check for the actual response
@app.route("/pythonbotz/check", methods=["GET"])
def check_response():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id parameter is required"}), 400

    if user_id in pending_responses:
        reply = pending_responses.pop(user_id)  # Remove after fetching
        return jsonify({"reply": reply, "Owner": "@PythonBotz"})
    else:
        return jsonify({"reply": "Fetching response...", "Owner": "@PythonBotz"})

if __name__ == "__main__":
    app.run(debug=True)