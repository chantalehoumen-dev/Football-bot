from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY")
BASE_URL = "https://v3.football.api-sports.io"

headers = {
    "x-apisports-key": API_KEY
}

@app.route("/")
def home():
    return "Football-bot PRO actif ⚽🔥"

@app.route("/matchs-du-jour")
def matchs_du_jour():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"{BASE_URL}/fixtures?date={today}"
    
    response = requests.get(url, headers=headers)
    data = response.json()

    if "response" not in data:
        return jsonify({"erreur": "Problème API ou clé invalide"})

    matchs = []

    for match in data["response"]:
        team1 = match["teams"]["home"]["name"]
        team2 = match["teams"]["away"]["
