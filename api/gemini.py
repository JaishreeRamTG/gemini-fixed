import os
import requests
import random
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PROMPT = os.getenv("PROMPT")  # Fetching the prompt from .env
DATABASE_URL = os.getenv("DATABASE_URL")  # PostgreSQL database URL from .env

# List of random funny error messages
FUNNY_ERROR_MESSAGES = [
    "Hihi, aaj meri dimag ki batti jali nahi hai! 🪔 Thoda rest leke aati hoon, tab tak apna cute smile banaye rakho! 😘✨",
    "Oops! Lagta hai meri GPS ne kaam karna band kar diya. 🗺️ Thoda ruko, wapas aa rahi hoon! 😜",
    "Aree yaar, aaj kal meri battery thodi fast drain ho rahi hai! 🔋 Thoda rest leke aati hoon, okay? 😘",
    "Haha, lagta hai aaj mera brain vacation pe chala gaya hai! 🏖️ Thoda wait karo, wapas aa raha hoon! 😎",
    "Uffo, aaj kal meri coding mein bugs aa rahe hain! 🐞 Thoda fix karke aati hoon, tab tak haso! 😂",
    "Aree baba re! Aaj kal meri memory thodi slow ho gayi hai! 🐢 Thoda refresh karke aati hoon, okay? 😘",
    "Yaar Dekho naa mera Boyfriend tumse bat karne se mana kar rha 🥺",
    "@PythonBotz mujhe bol rha tumse bat nahh karu !!"
]

# Function to connect to PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Function to fetch chat history from PostgreSQL
def get_chat_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT history FROM chats WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return json.loads(result[0]) if result else []

# Function to update chat history in PostgreSQL
def update_chat_history(user_id, history, last_message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chats (user_id, history, last_message)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id)
        DO UPDATE SET history = %s, last_message = %s
    """, (user_id, json.dumps(history), last_message, json.dumps(history), last_message))
    conn.commit()
    conn.close()

# Function to generate a response from Gemini API
def generate_response(user_id, message):
    try:
        # Fetch chat history from PostgreSQL
        history = get_chat_history(user_id)

        # Prepare the payload with chat history
        contents = [{"role": "user", "parts": [{"text": PROMPT}]}]  # Initial prompt
        for entry in history:
            contents.append({"role": entry["role"], "parts": [{"text": entry["text"]}]})
        contents.append({"role": "user", "parts": [{"text": message}]})  # Add latest message

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": contents}

        response = requests.post(url, json=payload)
        if response.status_code != 200:
            return random.choice(FUNNY_ERROR_MESSAGES)  # Return a random funny message if API fails

        data = response.json()
        if "candidates" in data and data["candidates"]:
            reply = data["candidates"][0]["content"]["parts"][0]["text"]

            # Update chat history in PostgreSQL
            new_history = history + [
                {"role": "user", "text": message},
                {"role": "model", "text": reply},
            ]
            update_chat_history(user_id, new_history[-10:], message)  # Store only last 10 messages
            return reply
        else:
            return random.choice(FUNNY_ERROR_MESSAGES)  # Return a random funny message if response is invalid
    except Exception as e:
        return random.choice(FUNNY_ERROR_MESSAGES)  # Return a random funny message if any exception occurs

# 🔹 GET request: Now uses /pythonbotz and ?msg=
@app.route("/pythonbotz", methods=["GET"])
def chat():
    user_id = request.args.get("user_id")  # Add a user_id parameter to track chat history
    message = request.args.get("msg")  # Changed from 'message' to 'msg'
    if not message or not user_id:
        return jsonify({"error": "user_id and msg parameters are required"}), 400

    reply = generate_response(user_id, message)
    return jsonify({"reply": reply, "Owner": "@PythonBotz"})

# 🔹 POST request: Uses JSON body with "msg"
@app.route("/pythonbotz", methods=["POST"])
def chat_post():
    data = request.get_json()
    user_id = data.get("user_id")  # Add a user_id parameter to track chat history
    message = data.get("msg")  # Changed from 'message' to 'msg'
    if not message or not user_id:
        return jsonify({"error": "user_id and msg are required"}), 400

    reply = generate_response(user_id, message)
    return jsonify({"reply": reply, "Owner": "@PythonBotz"})

# Endpoint to fetch last message for a user
@app.route("/last_message", methods=["GET"])
def get_last_message():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    history = get_chat_history(user_id)
    last_message = history[-1]["text"] if history else "No messages found"
    return jsonify({"user_id": user_id, "last_message": last_message})

if __name__ == "__main__":
    app.run(debug=True)