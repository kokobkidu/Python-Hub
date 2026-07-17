from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    url = "https://v3.football.api-sports.io/fixtures?league=39&season=2023"
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': 'e9a95b775eba7237f2a107a30bad87f9'
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        # ውጤቱን በ HTML ሰንጠረዥ መልክ እናዘጋጀው
        html = "<h1>የእግር ኳስ ውጤቶች (Premier League 2023)</h1>"
        html += "<table border='1'><tr><th>ቤት</th><th>ውጤት</th><th>ሜዳ</th></tr>"
        
        for fixture in data['response']:
            home_team = fixture['teams']['home']['name']
            away_team = fixture['teams']['away']['name']
            goals_home = fixture['goals']['home']
            goals_away = fixture['goals']['away']
            
            html += f"<tr><td>{home_team} vs {away_team}</td><td>{goals_home} - {goals_away}</td><td>{fixture['fixture']['venue']['name']}</td></tr>"
        
        html += "</table>"
        return html
        
    except Exception as e:
        return f"ስህተት ተፈጥሯል: {str(e)}"

if __name__ == '__main__':
    app.run()
