from flask import Flask, request
import requests
import os

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY")

headers = {
    "x-apisports-key": API_KEY
}

BASE_URL = "https://v3.football.api-sports.io"

@app.route("/")
def home():
    return "Football-bot PRO actif"

def get_team_id(team_name):
    url = f"{BASE_URL}/teams?search={team_name}"
    response = requests.get(url, headers=headers)
    data = response.json()

    if data["results"] == 0:
        return None

    return data["response"][0]["team"]["id"]

@app.route("/analyse")
def analyse():
    team1 = request.args.get("team1")
    team2 = request.args.get("team2")

    if not team1 or not team2:
        return "Veuillez fournir team1 et team2"

    team1_id = get_team_id(team1)
    team2_id = get_team_id(team2)

    if not team1_id or not team2_id:
        return "Équipe introuvable"

    # 5 derniers matchs équipe 1
    url1 = f"{BASE_URL}/fixtures?team={team1_id}&last=5"
    data1 = requests.get(url1, headers=headers).json()

    # 5 derniers matchs équipe 2
    url2 = f"{BASE_URL}/fixtures?team={team2_id}&last=5"
    data2 = requests.get(url2, headers=headers).json()

    # Confrontations directes
    url_h2h = f"{BASE_URL}/fixtures/headtohead?h2h={team1_id}-{team2_id}&last=5"
    data_h2h = requests.get(url_h2h, headers=headers).json()

    result = f"\n===== ANALYSE {team1} vs {team2} =====\n\n"

    result += "----- 5 derniers matchs " + team1 + " -----\n"
    for match in data1["response"]:
        result += f'{match["teams"]["home"]["name"]} {match["goals"]["home"]} - {match["goals"]["away"]} {match["teams"]["away"]["name"]}\n'

    result += "\n----- 5 derniers matchs " + team2 + " -----\n"
    for match in data2["response"]:
        result += f'{match["teams"]["home"]["name"]} {match["goals"]["home"]} - {match["goals"]["away"]} {match["teams"]["away"]["name"]}\n'

    result += "\n----- 5 dernières confrontations directes -----\n"
    for match in data_h2h["response"]:
        result += f'{match["teams"]["home"]["name"]} {match["goals"]["home"]} - {match["goals"]["away"]} {match["teams"]["away"]["name"]}\n'

    return result

if __name__ == "__main__":
    app.run()
