from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    url = "https://v3.football.api-sports.io/fixtures?league=39&season=2023
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': 'e9a95b775eba7237f2a107a30bad87f9'
    }
    try:
        response = requests.get(url, headers=headers)
        # ኮዱ እዚህ ጋር ነው የሚስተካከለው
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)})
