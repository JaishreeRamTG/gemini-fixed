from fastapi import FastAPI, Request
import httpx

app = FastAPI()

API_URL = "https://gemini-fixed.vercel.app/pythonbotz?msg={}"

@app.get("/")
async def home():
    return {"message": "Bot is running!"}

@app.get("/chat")
async def chat(msg: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL.format(msg))
        data = response.json()
    
    return {"reply": data.get("reply", "No response available.")}