from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    # የሙከራ ግጥሚያዎች መረጃ (በነፃው ፕላን ምትክ ዲዛይኑን ለማየት)
    matches = [
        {"home": "Manchester United", "away": "Arsenal", "home_goals": 2, "away_goals": 1, "status": "Finished (FT)"},
        {"home": "Chelsea", "away": "Liverpool", "home_goals": 0, "away_goals": 0, "status": "Finished (FT)"},
        {"home": "Manchester City", "away": "Tottenham", "home_goals": 3, "away_goals": 2, "status": "Finished (FT)"},
        {"home": "Newcastle United", "away": "Aston Villa", "home_goals": "-", "away_goals": "-", "status": "10:30 PM"},
        {"home": "Brighton", "away": "West Ham", "home_goals": 1, "away_goals": 1, "status": "Second Half"}
    ]
    
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
        </style>
    </head>
    <body>
        <div class="header">⚽ Premier League Live</div>
    """
    
    for match in matches:
        html_content += f"""
        <div class="match-card">
            <div class="team home">{match['home']}</div>
            <div class="score-box">
                {match['home_goals']} - {match['away_goals']}
                <div class="match-status">{match['status']}</div>
            </div>
            <div class="team away">{match['away']}</div>
        </div>
        """
        
    html_content += """
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    app.run()
