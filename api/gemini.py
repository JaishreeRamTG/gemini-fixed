import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Fetch API key and prompt from .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PROMPT = os.getenv("PROMPT")

# In-memory chat history storage
chat_history = {}

def generate_response(user_id, message):
    try:
        if not GEMINI_API_KEY:
            return "Error: GEMINI_API_KEY is not set in the environment."

        if not PROMPT:
            return "Error: Prompt is missing in the environment."

        # Fetch user's chat history
        history = chat_history.get(user_id, [])

        # Construct payload for API request
        contents = [{"role": "user", "parts": [{"text": PROMPT}]}]
        for entry in history:
            contents.append({"role": entry["role"], "parts": [{"text": entry["text"]}]})
        contents.append({"role": "user", "parts": [{"text": message}]})

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": contents}
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=payload, headers=headers)

        # Handle API errors
        if response.status_code != 200:
            return f"Error: API request failed with status {response.status_code}. Please try again later."

        data = response.json()

        # Extract response
        if "candidates" in data and data["candidates"]:
            reply = data["candidates"][0]["content"]["parts"][0]["text"]

            # Update chat history
            chat_history[user_id] = history + [
                {"role": "user", "parts": [{"text": message}]},
                {"role": "model", "parts": [{"text": reply}]},
            ]
            return reply
        else:
            return "Error: Received an invalid response from the API."

    except Exception as e:
        return f"Error: {str(e)}"

# ✅ GET Route
@app.route("/pythonbotz", methods=["GET"])
def chat():
    user_id = request.args.get("user_id")
    message = request.args.get("msg")

    if not user_id or not message:
        return jsonify({"error": "user_id and msg parameters are required"}), 400

    reply = generate_response(user_id, message)
    return jsonify({"reply": reply, "Owner": "@PythonBotz"})

# ✅ POST Route
@app.route("/pythonbotz", methods=["POST"])
def chat_post():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    user_id = data.get("user_id")
    message = data.get("msg")

    if not user_id or not message:
        return jsonify({"error": "user_id and msg are required"}), 400

    reply = generate_response(user_id, message)
    return jsonify({"reply": reply, "Owner": "@PythonBotz"})

# ✅ Flask App Runner
if __name__ == "__main__":
    app.run(debug=True)