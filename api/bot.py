from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

API_URL = "https://gemini-fixed.vercel.app/pythonbotz?msg={}"

@app.post("/bot/")
async def chatbot(message: dict):
    if "message" not in message:
        raise HTTPException(status_code=400, detail="Message field is required")

    user_message = message["message"]
    
    try:
        response = requests.get(API_URL.format(user_message))
        return {"reply": response.text}
    except requests.RequestException:
        raise HTTPException(status_code=500, detail="Failed to fetch response")