from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"

headers = {
    "x-apisports-key": API_KEY
}

def get_team_id(team_name):
    response = requests.get(f"{BASE_URL}/teams?search={team_name}", headers=headers)
    data = response.json()
    if data["results"] > 0:
        return data["response"][0]["team"]["id"]
    return None

def get_last_matches(team_id):
    response = requests.get(f"{BASE_URL}/fixtures?team={team_id}&last=10", headers=headers)
    return response.json()

@app.route("/analyse", methods=["GET"])
def analyse():
    team1 = request.args.get("team1")
    team2 = request.args.get("team2")

    id1 = get_team_id(team1)
    id2 = get_team_id(team2)

    if not id1 or not id2:
        return jsonify({"error": "Equipe introuvable"})

    data1 = get_last_matches(id1)
    data2 = get_last_matches(id2)

    return jsonify({
        "team1_last_matches": data1,
        "team2_last_matches": data2
    })

@app.route("/")
def home():
    return "Bot Analyse Football Actif 🔥"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
