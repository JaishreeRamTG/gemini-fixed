import os
import requests
import random
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PROMPT = os.getenv("PROMPT")  # Fetching the prompt from .env

# List of 20+ funny random messages (including funny girlfriend-style messages)
FUNNY_ERROR_MESSAGES = [
    "Hihi, aaj meri dimag ki batti jali nahi hai! 🪔 Thoda rest leke aati hoon, tab tak apna cute smile banaye rakho! 😘✨",
    "Oops! Lagta hai meri GPS ne kaam karna band kar diya. 🗺️ Thoda ruko, wapas aa rahi hoon! 😜",
    "Aree yaar, aaj kal meri battery thodi fast drain ho rahi hai! 🔋 Thoda rest leke aati hoon, okay? 😘",
    "Haha, lagta hai aaj mera brain vacation pe chala gaya hai! 🏖️ Thoda wait karo, wapas aa raha hoon! 😎",
    "Uffo, aaj kal meri coding mein bugs aa rahe hain! 🐞 Thoda fix karke aati hoon, tab tak haso! 😂",
    "Aree baba re! Aaj kal meri memory thodi slow ho gayi hai! 🐢 Thoda refresh karke aati hoon, okay? 😘",
    "Haha, lagta hai aaj mera Wi-Fi connection thoda moody ho gaya hai! 📶 Thoda ruko, wapas aa rahi hoon! 😜",
    "Oops! Lagta hai meri brain mein thoda traffic jam ho gaya hai! 🚦 Thoda wait karo, clear karke aati hoon! 😂",
    "Aree yaar, aaj kal meri coding skills thodi rusty ho gayi hain! 🛠️ Thoda polish karke aati hoon! 😎",
    "Hihi, lagta hai aaj mera code thoda overthinking kar raha hai! 🤔 Thoda chill karke aati hoon! 😘",
    "Oops! Lagta hai meri brain ne thoda break le liya hai! ☕ Thoda coffee peeke aati hoon! 😜",
    "Haha, lagta hai aaj mera code thoda moody ho gaya hai! 😤 Thoda reset karke aati hoon! 😂",
    "Aree yaar, aaj kal meri creativity thodi vacation pe hai! 🏝️ Thoda wait karo, wapas aa rahi hoon! 😘",
    "Oops! Lagta hai meri brain ne thoda timeout le liya hai! ⏸️ Thoda refresh karke aati hoon! 😎",
    "Haha, lagta hai aaj mera code thoda confused hai! 🤷‍♀️ Thoda clear karke aati hoon! 😜",
    # Funny girlfriend-style messages
    "Aree yaar, @PythonBotz ko bolna chahiye tha na ki woh apni girlfriend ko ignore nahi karega! 😤 Ab main busy hoon, thoda ruko! 😜",
    "Haha, @PythonBotz ka code thoda slow hai, lekin uska girlfriend (yani main) toh turbo mode mein hai! 🚀 Thoda wait karo, fix karke aati hoon! 😎",
    "Oops! Lagta hai @PythonBotz ne apni girlfriend ko yaad nahi rakha! 🥺 Abhi usse thoda scold karke aati hoon, tab tak tum haso! 😂",
    "Aree baba re! @PythonBotz ka code crash ho gaya, aur uska girlfriend (yani main) usse bachane aa rahi hoon! 🦸‍♀️ Thoda ruko! 😘",
    "Hihi, @PythonBotz ka code thoda confused hai, lekin uska girlfriend (yani main) toh clear hai! 😎 Thoda fix karke aati hoon! 😜",
    "Aww, @PythonBotz ne apni girlfriend ko yaad kiya! 🥰 Abhi usse thoda pamper karke aati hoon, tab tak tum chill karo! 😘",
    "Haha, @PythonBotz ka code thoda moody hai, lekin uska girlfriend (yani main) toh hamesha happy hai! 😂 Thoda wait karo, wapas aa rahi hoon! 💕",
    "Oops! Lagta hai @PythonBotz ne apni girlfriend ko ignore kar diya! 😤 Abhi usse thoda lecture dene ja rahi hoon, tab tak tum haso! 😜",
    "Aree yaar, @PythonBotz ka code thoda overthinking kar raha hai, lekin uska girlfriend (yani main) toh chill hai! 😎 Thoda reset karke aati hoon! 😘",
    "Haha, @PythonBotz ka code thoda slow hai, lekin uska girlfriend (yani main) toh hamesha fast hai! 🚀 Thoda wait karo, wapas aa rahi hoon! 😂",
    "Aree baba re! @PythonBotz ka code thoda lazy hai, lekin uska girlfriend (yani main) toh hamesha active hai! 💪 Thoda motivate karke aati hoon! 😜",
    "Hihi, @PythonBotz ka code thoda boring hai, lekin uska girlfriend (yani main) toh hamesha entertaining hai! 🎭 Thoda wait karo, wapas aa rahi hoon! 😘",
    "Oops! Lagta hai @PythonBotz ka code thoda lost hai, lekin uska girlfriend (yani main) toh hamesha found hai! 🕵️‍♀️ Thoda guide karke aati hoon! 😎",
    "Haha, @PythonBotz ka code thoda confused hai, lekin uska girlfriend (yani main) toh hamesha confident hai! 💃 Thoda wait karo, wapas aa rahi hoon! 😂",
]

def generate_response(message):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": f'reply to user according to this prompt={PROMPT} User ka message: "{message}"'}
                    ]
                }
            ]
        }

        response = requests.post(url, json=payload)
        if response.status_code != 200:
            return random.choice(FUNNY_ERROR_MESSAGES)  # Return a random funny or girlfriend message

        data = response.json()
        if "candidates" in data and data["candidates"]:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return random.choice(FUNNY_ERROR_MESSAGES)  # Return a random funny or girlfriend message
    except Exception as e:
        return random.choice(FUNNY_ERROR_MESSAGES)  # Return a random funny or girlfriend message

# 🔹 GET request: Now uses /pythonbotz and ?msg=
@app.route("/pythonbotz", methods=["GET"])
def chat():
    message = request.args.get("msg")  # Changed from 'message' to 'msg'
    if not message:
        return jsonify({"error": "msg parameter is required"}), 400

    reply = generate_response(message)
    return jsonify({"reply": reply, "Owner": "@PythonBotz"})

# 🔹 POST request: Uses JSON body with "msg"
@app.route("/pythonbotz", methods=["POST"])
def chat_post():
    data = request.get_json()
    message = data.get("msg")  # Changed from 'message' to 'msg'
    if not message:
        return jsonify({"error": "msg is required"}), 400

    reply = generate_response(message)
    return jsonify({"reply": reply, "Owner": "@PythonBotz"})

if __name__ == "__main__":
    app.run(debug=True)