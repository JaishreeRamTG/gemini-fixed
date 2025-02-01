import json
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

def deepsex(query):
    url = "https://api.blackbox.ai/api/chat"
    payload = {
        "messages": [{
            "role": "user",
            "content": query
        }],
        "userSelectedModel": "deepseek-v3",
        "validated": "10f37b34-a166-4efb-bce5-1312d87f2f94"
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

@app.route("/pythonbotz", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        query = request.form["query"]
        response = deepsex(query)
        return render_template("index.html", query=query, response=response)
    return render_template("index.html", query=None, response=None)

# Entry point for the Vercel serverless function
def handler(request):
    with app.request_context(request):
        return app.full_dispatch_request()