import os
import requests
import random
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PROMPT = os.getenv("PROMPT")  # Fetching the prompt from .env
MONGO_URI = "mongodb+srv://Outlawbots:Zoro@cluster0.huekk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["ChatBotDB"]
chat_collection = db["chats"]

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

def generate_response(user_id, message):
    try:
        # Fetch chat history from MongoDB
        user_data = chat_collection.find_one({"user_id": user_id})
        history = user_data.get("history", []) if user_data else []

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

            # Update chat history in MongoDB
            new_history = history + [
                {"role": "user", "text": message},
                {"role": "model", "text": reply},
            ]

            chat_collection.update_one(
                {"user_id": user_id},
                {"$set": {"history": new_history[-10:], "last_message": message}},  # Store only last 10 messages
                upsert=True
            )
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

    user_data = chat_collection.find_one({"user_id": user_id})
    last_message = user_data.get("last_message", "No messages found") if user_data else "No messages found"

    return jsonify({"user_id": user_id, "last_message": last_message})

if __name__ == "__main__":
    app.run(debug=True)