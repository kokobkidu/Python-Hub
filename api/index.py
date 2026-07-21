from flask import Flask, render_template_string, request
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def home():
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # የ7 ቀናት ማጣሪያ (Yesterday, Today, Tomorrow እና ሌሎች ቀናት)
    dates_list = []
    base_date = datetime.now() - timedelta(days=3)
    for i in range(7):
        d = base_date + timedelta(days=i)
        d_str = d.strftime('%Y-%m-%d')
        d_label = d.strftime('%a %d %b')
        dates_list.append({'date': d_str, 'label': d_label})
    
    # ለእያንዳንዱ ቀን የተለዩ እና እውነተኛ ሊመስሉ የሚችሉ የጨዋታ መርሃ-ግብሮች እና ዝርዝሮች
    matches_db = {
        (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'): [
            {"league": "🇪🇸 Spanish La Liga - Yesterday", "home": "Real Madrid", "away": "Barcelona", "h_goals": 3, "a_goals": 1, "status": "FT", "detail": "Goals: V. Junior 12', 45', R. Lewandowski 30' (Pen)"},
            {"league": "🇮🇹 Italian Serie A - Yesterday", "home": "AC Milan", "away": "Inter Milan", "h_goals": 2, "a_goals": 2, "status": "FT", "detail": "Goals: O. Giroud 15', H. Çalhanoğlu 55'"}
        ],
        datetime.now().strftime('%Y-%m-%d'): [
            {"league": "🏆 English Premier League - Today (Live)", "home": "Manchester United", "away": "Arsenal", "h_goals": 2, "a_goals": 1, "status": "78'", "detail": "Live Match - Yellow Card: B. Saka 45'"},
            {"league": "🏆 English Premier League - Today (Live)", "home": "Chelsea", "away": "Liverpool", "h_goals": 0, "a_goals": 0, "status": "HT", "detail": "First half ended - Possession: 48% - 52%"},
            {"league": "🤝 Club Friendly - Today", "home": "FC Tokyo", "away": "Nagoya Grampus", "h_goals": 2, "a_goals": 1, "status": "FT", "detail": "Friendly Match - Full Time"},
            {"league": "⚽ Women's International", "home": "USA Women", "away": "Brazil Women", "h_goals": 3, "a_goals": 2, "status": "FT", "detail": "International Friendly Women"}
        ],
        (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'): [
            {"league": "🏆 UEFA Champions League - Tomorrow", "home": "Bayern Munich", "away": "PSG", "h_goals": "-", "a_goals": "-", "status": "11:45 PM", "detail": "Quarter Final - Preview & Stats"},
            {"league": "🇩🇪 German Bundesliga - Tomorrow", "home": "Dortmund", "away": "RB Leipzig", "h_goals": "-", "a_goals": "-", "status": "9:30 PM", "detail": "Regular Season Match"}
        ]
    }
    
    # ለተመረጠው ቀን ዳታ ካለ ማምጣት፣ ከሌለ ደግሞ አጠቃላይ መደበኛ ጨዋታዎችን ማሳየት
    matches = matches_db.get(selected_date, [
        {"league": "🌍 International Fixtures", "home": "Local All-Stars", "away": "Global XI", "h_goals": 1, "a_goals": 1, "status": "FT", "detail": "Exhibition Match"},
        {"league": "⚽ Regional Cup", "home": "City Rovers", "away": "United FC", "h_goals": 0, "a_goals": 2, "status": "FT", "detail": "Cup Knockout stage"}
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
            
            .match-card {{ background: white; margin-bottom: 8px; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            .match-main {{ display: flex; justify-content: space-between; align-items: center; }}
            .team {{ width: 38%; font-weight: bold; font-size: 13px; color: #333; display: flex; align-items: center; }}
            .team.home {{ justify-content: flex-end; text-align: right; }}
            .team.away {{ justify-content: flex-start; text-align: left; }}
            
            .score-box {{ width: 24%; text-align: center; background: #e8f5e9; padding: 6px; border-radius: 4px; font-weight: bold; font-size: 15px; color: #2e7d32; border: 1px solid #c8e6c9; }}
            .match-status {{ font-size: 9px; color: #666; margin-top: 3px; text-transform: uppercase; }}
            
            .match-detail {{ font-size: 11px; color: #555; background: #f9f9f9; margin-top: 8px; padding: 6px; border-radius: 4px; border-left: 3px solid #2e7d32; }}
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
    
    current_league = ""
    for match in matches:
        if match['league'] != current_league:
            current_league = match['league']
            html_content += f'<div class="league-title">🏆 {current_league}</div>'
            
        html_content += f"""
        <div class="match-card">
            <div class="match-main">
                <div class="team home"><span>{match['home']}</span></div>
                <div class="score-box">
                    {match['h_goals']} - {match['a_goals']}
                    <div class="match-status">{match['status']}</div>
                </div>
                <div class="team away"><span>{match['away']}</span></div>
            </div>
            <div class="match-detail">📌 {match['detail']}</div>
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
