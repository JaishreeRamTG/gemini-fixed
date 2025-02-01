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
        # Fetch the user's chat history
        history = chat_history.get(user_id, [])

        # Prepare the payload with chat history
        contents = [{"role": "user", "parts": [{"text": PROMPT}]}]  # Add the initial prompt
        for entry in history:
            contents.append({"role": entry["role"], "parts": [{"text": entry["text"]}]})
        contents.append({"role": "user", "parts": [{"text": message}]})  # Add the latest message

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": contents}

        response = requests.post(url, json=payload)
        if response.status_code != 200:
            pending_responses[user_id] = "Error: Unable to fetch response at the moment."
            return

        data = response.json()
        if "candidates" in data and data["candidates"]:
            reply = data["candidates"][0]["content"]["parts"][0]["text"]

            # Update chat history
            chat_history[user_id] = history + [
                {"role": "user", "parts": [{"text": message}]},
                {"role": "model", "parts": [{"text": reply}]},
            ]

            # Store the response temporarily
            pending_responses[user_id] = reply
        else:
            pending_responses[user_id] = "Error: Unable to fetch response at the moment."
    except Exception:
        pending_responses[user_id] = "Error: Unable to fetch response at the moment."

def process_chat_request(user_id, message):
    """Starts a separate thread to process chat response asynchronously."""
    thread = threading.Thread(target=generate_response, args=(user_id, message))
    thread.start()

# 🔹 GET request: Uses /pythonbotz and ?msg=
@app.route("/pythonbotz", methods=["GET"])
def chat():
    user_id = request.args.get("user_id")  # Add a user_id parameter to track chat history
    message = request.args.get("msg")  # Changed from 'message' to 'msg'
    if not message or not user_id:
        return jsonify({"error": "user_id and msg parameters are required"}), 400

    # Start processing the chat request in a separate thread
    process_chat_request(user_id, message)

    return jsonify({"reply": "Fetching response...", "Owner": "@PythonBotz"})

# 🔹 GET response check: Users can poll for the actual response
@app.route("/pythonbotz/check", methods=["GET"])
def check_response():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id parameter is required"}), 400

    # Check if the response is ready
    if user_id in pending_responses:
        reply = pending_responses.pop(user_id)  # Remove after fetching
        return jsonify({"reply": reply, "Owner": "@PythonBotz"})
    else:
        return jsonify({"reply": "Fetching response...", "Owner": "@PythonBotz"})

# 🔹 POST request: Uses JSON body with "msg"
@app.route("/pythonbotz", methods=["POST"])
def chat_post():
    data = request.get_json()
    user_id = data.get("user_id")  # Add a user_id parameter to track chat history
    message = data.get("msg")  # Changed from 'message' to 'msg'
    if not message or not user_id:
        return jsonify({"error": "user_id and msg are required"}), 400

    # Start processing the chat request in a separate thread
    process_chat_request(user_id, message)

    return jsonify({"reply": "Fetching response...", "Owner": "@PythonBotz"})

# 🔹 POST response check: Users can poll for the actual response
@app.route("/pythonbotz/check", methods=["POST"])
def check_response_post():
    data = request.get_json()
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    # Check if the response is ready
    if user_id in pending_responses:
        reply = pending_responses.pop(user_id)  # Remove after fetching
        return jsonify({"reply": reply, "Owner": "@PythonBotz"})
    else:
        return jsonify({"reply": "Fetching response...", "Owner": "@PythonBotz"})

if __name__ == "__main__":
    app.run(debug=True)