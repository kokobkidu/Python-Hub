from flask import Flask, render_template_string, request
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def home():
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # አናት ላይ የሚታዩት የቀናት ማጣሪያዎች (ከ Besoccer የቀዳነው ዲዛይን)
    dates_list = []
    base_date = datetime.now() - timedelta(days=2)
    for i in range(7):
        d = base_date + timedelta(days=i)
        d_str = d.strftime('%Y-%m-%d')
        d_label = d.strftime('%a %d %b')
        dates_list.append({'date': d_str, 'label': d_label})
    
    # Koki Score የሚጠቀምባቸው የናሙና ግጥሚያዎች (ሊግ፣ ፍሬንድሊ እና የሴቶች ጨዋታዎችን ጨምሮ)
    sample_matches = {
        datetime.now().strftime('%Y-%m-%d'): [
            {"category": "🏆 English Premier League", "home": "Manchester United", "away": "Arsenal", "h_score": 2, "a_score": 1, "status": "FT"},
            {"category": "🏆 English Premier League", "home": "Chelsea", "away": "Liverpool", "h_score": 0, "a_score": 0, "status": "FT"},
            {"category": "🤝 Club Friendly", "home": "FC Tokyo", "away": "Nagoya Grampus", "h_score": 2, "a_score": 1, "status": "FT"},
            {"category": "🤝 Club Friendly", "home": "Ryūkyū", "away": "Shonan Bellmare", "h_score": "-", "a_score": "-", "status": "10:30 PM"},
            {"category": "⚽ Women's International", "home": "USA Women", "away": "Brazil Women", "h_score": 3, "a_score": 2, "status": "FT"}
        ],
        (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'): [
            {"category": "🏆 Spanish La Liga", "home": "Real Madrid", "away": "Barcelona", "h_score": 1, "a_score": 3, "status": "FT"},
            {"category": "🤝 Club Friendly", "home": "Brinje-Grosuplje", "away": "FK Epitsentr", "h_score": 2, "a_score": 3, "status": "FT"}
        ],
        (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'): [
            {"category": "🏆 UEFA Champions League", "home": "Bayern Munich", "away": "PSG", "h_score": "-", "a_score": "-", "status": "11:45 PM"},
            {"category": "🏆 Italian Serie A", "home": "AC Milan", "away": "Inter Milan", "h_score": "-", "a_score": "-", "status": "9:00 PM"}
        ]
    }
    
    # ለተመረጠው ቀን ግጥሚያ ካለ ማምጣት፣ ካለፈ ወይም ከሌለ ነባሪ ማሳየት
    matches = sample_matches.get(selected_date, [
        {"category": "🤝 International Friendly", "home": "Local XI", "away": "All Stars", "h_score": 1, "a_score": 1, "status": "FT"},
        {"category": "⚽ Women's League", "home": "City Girls", "away": "United Ladies", "h_score": 2, "a_score": 0, "status": "FT"}
    ])
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Koki Score</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 0; }}
            .top-bar {{ background-color: #2e7d32; color: white; padding: 12px; text-align: center; font-size: 19px; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            
            .date-tabs {{ display: flex; background-color: #388e3c; overflow-x: auto; white-space: nowrap; scrollbar-width: none; }}
            .date-tabs::-webkit-scrollbar {{ display: none; }}
            .date-tab {{ color: #c8e6c9; padding: 12px 16px; text-decoration: none; font-size: 12px; font-weight: bold; text-align: center; display: inline-block; border-bottom: 3px solid transparent; }}
            .date-tab.active {{ color: white; border-bottom: 3px solid white; background-color: rgba(255,255,255,0.15); }}
            
            .container {{ padding: 10px; max-width: 600px; margin: auto; }}
            .league-title {{ font-size: 12px; font-weight: bold; color: #333; margin: 15px 5px 6px 5px; text-transform: uppercase; background: #e0e0e0; padding: 6px 10px; border-radius: 4px; }}
            
            .match-card {{ background: white; margin-bottom: 8px; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }}
            .team {{ width: 38%; font-weight: bold; font-size: 13px; color: #333; display: flex; align-items: center; }}
            .team.home {{ justify-content: flex-end; text-align: right; }}
            .team.away {{ justify-content: flex-start; text-align: left; }}
            
            .score-box {{ width: 24%; text-align: center; background: #e8f5e9; padding: 6px; border-radius: 4px; font-weight: bold; font-size: 15px; color: #2e7d32; border: 1px solid #c8e6c9; }}
            .match-status {{ font-size: 9px; color: #666; margin-top: 3px; text-transform: uppercase; }}
        </style>
    </head>
    <body>
        <div class="top-bar">⚽ Koki Score</div>
        
        <div class="date-tabs">
    """
    
    for d in dates_list:
        is_active = "active" if d['date'] == selected_date else ""
        html_content += f'<a href="/?date={d["date"]}" class="date-tab {is_active}">{d["label"]}</a>'
        
    html_content += """
        </div>
        <div class="container">
    """
    
    current_cat = ""
    for match in matches:
        if match['category'] != current_cat:
            current_cat = match['category']
            html_content += f'<div class="league-title">{current_cat}</div>'
            
        html_content += f"""
        <div class="match-card">
            <div class="team home"><span>{match['home']}</span></div>
            <div class="score-box">
                {match['h_score']} - {match['a_score']}
                <div class="match-status">{match['status']}</div>
            </div>
            <div class="team away"><span>{match['away']}</span></div>
        </div>
        """
        
    html_content += """
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    app.run()
