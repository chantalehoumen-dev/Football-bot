from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
API_HOST = "api-football-v1.p.rapidapi.com"

LEAGUES = [39, 140, 135, 78, 61]  # PL, Liga, Serie A, Bundesliga, Ligue 1
SEASON = 2024

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": API_HOST
}

def get_team_id(team_name):
    url = f"https://{API_HOST}/v3/teams"
    querystring = {"search": team_name}
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    if data["response"]:
        return data["response"][0]["team"]["id"]
    return None

def get_last_matches(team_id):
    url = f"https://{API_HOST}/v3/fixtures"
    querystring = {
        "team": team_id,
        "season": SEASON,
        "last": 10
    }
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    return data["response"]

def analyze_matches(matches):
    total_goals = 0
    ht_goals = 0
    scores = []

    for match in matches:
        home = match["goals"]["home"] or 0
        away = match["goals"]["away"] or 0
        ht_home = match["score"]["halftime"]["home"] or 0
        ht_away = match["score"]["halftime"]["away"] or 0

        total_goals += home + away
        ht_goals += ht_home + ht_away
        scores.append(f"{home}-{away}")

    avg_goals = round(total_goals / len(matches), 2) if matches else 0
    avg_ht_goals = round(ht_goals / len(matches), 2) if matches else 0

    return {
        "scores_10_derniers_matchs": scores,
        "moyenne_buts_match": avg_goals,
        "moyenne_buts_mi_temps": avg_ht_goals
    }

@app.route("/analyse")
def analyse():
    team1 = request.args.get("team1")
    team2 = request.args.get("team2")

    id1 = get_team_id(team1)
    id2 = get_team_id(team2)

    if not id1 or not id2:
        return jsonify({"error": "Equipe non trouvée"})

    matches1 = get_last_matches(id1)
    matches2 = get_last_matches(id2)

    stats1 = analyze_matches(matches1)
    stats2 = analyze_matches(matches2)

    prediction = f"{round(stats1['moyenne_buts_match']/2)}-{round(stats2['moyenne_buts_match']/2)}"

    return jsonify({
        "equipe1": team1,
        "equipe2": team2,
        "stats_equipe1": stats1,
        "stats_equipe2": stats2,
        "prediction_score_estime": prediction
    })

@app.route("/")
def home():
    return "Football-bot PRO actif !"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
