from flask import Flask, render_template_string
import requests

app = Flask(__name__)

@app.route('/')
def home():
    # ትክክለኛውን የ API ሊንክ እና የራስ-መረጃ (Headers) እዚህ እናስገባለን
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': '2569736eeedf66e94d33e0afffa3694a'
    }
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Livescore - Football Matches</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 10px; }
            .header { background-color: #2e7d32; color: white; padding: 15px; text-align: center; font-size: 20px; font-weight: bold; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .match-card { background: white; margin-bottom: 10px; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }
            .team { width: 38%; font-weight: bold; font-size: 13px; color: #333; }
            .team.home { text-align: right; }
            .team.away { text-align: left; }
            .score-box { width: 24%; text-align: center; background: #e8f5e9; padding: 8px; border-radius: 5px; font-weight: bold; font-size: 16px; color: #2e7d32; }
            .match-status { font-size: 10px; color: #666; margin-top: 4px; text-transform: uppercase; }
            .no-match { text-align: center; padding: 20px; color: #666; font-weight: bold; background: white; border-radius: 8px; }
        </style>
    </head>
    <body>
        <div class="header">⚽ Live Football Matches</div>
    """
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        matches = data.get('response', [])
        
        if matches:
            for match in matches:
                home_team = match['teams']['home']['name']
                away_team = match['teams']['away']['name']
                
                home_goals = match['goals']['home']
                away_goals = match['goals']['away']
                
                status = match['fixture']['status']['short']
                elapsed = match['fixture']['status']['elapsed']
                
                h_score = home_goals if home_goals is not None else 0
                a_score = away_goals if away_goals is not None else 0
                
                match_status = f"{elapsed}'" if elapsed else status

                html_content += f"""
                <div class="match-card">
                    <div class="team home">{home_team}</div>
                    <div class="score-box">
                        {h_score} - {a_score}
                        <div class="match-status">{match_status}</div>
                    </div>
                    <div class="team away">{away_team}</div>
                </div>
                """
        else:
            html_content += '<div class="no-match">አሁን የሚደረግ የቀጥታ (Live) ግጥሚያ የለም</div>'
            
    except Exception as e:
        html_content += f'<div class="no-match">ስህተት ተፈጥሯል: {str(e)}</div>'
        
    html_content += """
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    app.run()
