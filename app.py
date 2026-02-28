from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"

headers = {
    "x-apisports-key": API_KEY
}

# 🔎 Récupérer ID équipe
def get_team_id(team_name):
    response = requests.get(
        f"{BASE_URL}/teams?search={team_name}",
        headers=headers
    )
    data = response.json()
    if data["results"] > 0:
        return data["response"][0]["team"]["id"]
    return None


# 📊 Récupérer 10 derniers matchs
def get_last_matches(team_id):
    response = requests.get(
        f"{BASE_URL}/fixtures?team={team_id}&last=10",
        headers=headers
    )
    return response.json()


# 📈 Analyse statistique simple
def analyze_matches(matches):
    total_goals = 0
    halftime_goals = 0
    scores = []

    for match in matches["response"]:
        ft_home = match["goals"]["home"] or 0
        ft_away = match["goals"]["away"] or 0
        ht_home = match["score"]["halftime"]["home"] or 0
        ht_away = match["score"]["halftime"]["away"] or 0

        total_goals += ft_home + ft_away
        halftime_goals += ht_home + ht_away

        scores.append(f"{ft_home}-{ft_away}")

    avg_goals = total_goals / 10 if total_goals else 0
    avg_ht_goals = halftime_goals / 10 if halftime_goals else 0

    return {
        "moyenne_buts_match": round(avg_goals, 2),
        "moyenne_buts_mi_temps": round(avg_ht_goals, 2),
        "derniers_scores": scores
    }


# ⚽ Route principale
@app.route("/analyse", methods=["GET"])
def analyse():
    team1 = request.args.get("team1")
    team2 = request.args.get("team2")

    if not team1 or not team2:
        return jsonify({"error": "Veuillez fournir team1 et team2"}), 400

    team1_id = get_team_id(team1)
    team2_id = get_team_id(team2)

    if not team1_id or not team2_id:
        return jsonify({"error": "Equipe non trouvée"}), 404

    matches1 = get_last_matches(team1_id)
    matches2 = get_last_matches(team2_id)

    analysis1 = analyze_matches(matches1)
    analysis2 = analyze_matches(matches2)

    # 🎯 Simulation simple score probable
    predicted_goals_team1 = round(analysis1["moyenne_buts_match"] / 2)
    predicted_goals_team2 = round(analysis2["moyenne_buts_match"] / 2)

    prediction = f"{predicted_goals_team1}-{predicted_goals_team2}"

    return jsonify({
        "equipe1": team1,
        "stats_equipe1": analysis1,
        "equipe2": team2,
        "stats_equipe2": analysis2,
        "prediction_score_probable": prediction
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
