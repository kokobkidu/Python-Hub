from flask import Flask, render_template_string
import requests

app = Flask(__name__)

@app.route('/')
def home():
    # ሲዝኑን ወደ 2024 ቀይረነዋል (ነፃው አካውንት እንዲያነበው)
    url = "https://v3.football.api-sports.io/fixtures?league=39&season=2024"
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': '2569736eeedf66e94d33e0afffa3694a'
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        matches = data.get('response', [])
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Livescore - Football Matches</title>
            <style>
                body { font-family: Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 10px; }
                .header { background-color: #2e7d32; color: white; padding: 15px; text-align: center; font-size: 20px; font-weight: bold; border-radius: 8px; margin-bottom: 15px; }
                .match-card { background: white; margin-bottom: 10px; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }
                .team { width: 40%; text-align: center; font-weight: bold; font-size: 14px; }
                .score-box { width: 20%; text-align: center; background: #e8f5e9; padding: 8px; border-radius: 5px; font-weight: bold; font-size: 16px; color: #2e7d32; }
                .match-status { font-size: 11px; color: #666; margin-top: 4px; }
            </style>
        </head>
        <body>
            <div class="header">⚽ Premier League Matches (2024)</div>
        """
        
        if matches:
            for match in matches:
                home_team = match['teams']['home']['name']
                away_team = match['teams']['away']['name']
                
                goals = match.get('goals', {})
                home_goals = goals.get('home')
                away_goals = goals.get('away')
                
                status = match['fixture']['status']['long']
                
                h_score = home_goals if home_goals is not None else "-"
                a_score = away_goals if away_goals is not None else "-"
                
                html_content += f"""
                <div class="match-card">
                    <div class="team">{home_team}</div>
                    <div class="score-box">
                        {h_score} - {a_score}
                        <div class="match-status">{status}</div>
                    </div>
                    <div class="team">{away_team}</div>
                </div>
                """
        else:
            html_content += "<p style='text-align:center;'>ለዚህ አመት የተገኘ ግጥሚያ የለም ወይም ፕላኑ ይገድበዋል</p>"
            
        html_content += """
        </body>
        </html>
        """
        return html_content

    except Exception as e:
        return f"ስህተት ተፈጥሯል: {str(e)}"

if __name__ == '__main__':
    app.run()
