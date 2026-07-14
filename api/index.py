from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    url = "https://v3.football.api-sports.io/fixtures?league=39&season=2023&last=5"
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': 'e9a95b77eba7237f2a107a30efca4dbb'
    }
    try:
        response = requests.get(url, headers=headers)
        # ኮዱ እዚህ ጋር ነው የሚስተካከለው
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run()
