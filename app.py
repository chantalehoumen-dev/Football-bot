from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
}

BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"

@app.route("/")
def home():
    return "Football-bot pro active"

def get_team_id(team_name):
    url = f"{BASE_URL}/teams"
    params = {"search": team_name}
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()
    if data["response"]:
        return data["response"][0]["team"]["id"]
    return None

def get_last_matches(team_id):
    url = f"{BASE_URL}/fixtures"
    params = {"team": team_id, "last": 10}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()

@app.route("/analyze")
def analyze():
    team1 = request.args.get("team1")
    team2 = request.args.get("team2")

    if not team1 or not team2:
        return jsonify({"error": "Provide team1 and team2"})

    team1_id = get_team_id(team1)
    team2_id = get_team_id(team2)

    if not team1_id or not team2_id:
        return jsonify({"error": "Team not found"})

    team1_matches = get_last_matches(team1_id)
    team2_matches = get_last_matches(team2_id)

    def extract_stats(matches):
        results = []
        total_goals = 0

        for match in matches["response"]:
            goals_home = match["goals"]["home"]
            goals_away = match["goals"]["away"]
            halftime_home = match["score"]["halftime"]["home"]
            halftime_away = match["score"]["halftime"]["away"]

            results.append({
                "fulltime": f"{goals_home}-{goals_away}",
                "halftime": f"{halftime_home}-{halftime_away}"
            })

            if goals_home is not None and goals_away is not None:
                total_goals += goals_home + goals_away

        avg_goals = total_goals / len(matches["response"]) if matches["response"] else 0

        return {
            "last_10": results,
            "average_goals": round(avg_goals, 2)
        }

    stats1 = extract_stats(team1_matches)
    stats2 = extract_stats(team2_matches)

    prediction = "Under 2.5 goals"
    if stats1["average_goals"] + stats2["average_goals"] > 4:
        prediction = "Over 2.5 goals"

    return jsonify({
        "team1": team1,
        "team2": team2,
        "team1_stats": stats1,
        "team2_stats": stats2,
        "prediction": prediction
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
