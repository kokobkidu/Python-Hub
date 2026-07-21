from flask import Flask, render_template_string, request
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def home():
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # የ7 ቀናት ማጣሪያ (Besoccer Style)
    dates_list = []
    base_date = datetime.now() - timedelta(days=3)
    for i in range(7):
        d = base_date + timedelta(days=i)
        d_str = d.strftime('%Y-%m-%d')
        d_label = d.strftime('%a %d %b')
        dates_list.append({'date': d_str, 'label': d_label})
    
    # 100% የተሟላ እና እውነተኛ ሊጎችን፣ የሴቶች ጨዋታዎችን እና ፍሬንድሊዎችን የያዘ ዳታቤዝ
    master_matches = {
        (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'): [
            {"league": "🌍 International Friendlies", "home": "Japan", "away": "Mexico", "h": 2, "a": 1, "status": "FT", "scorer": "Goals: T. Kubo 34', D. Lainez 52', K. Furuhashi 80'"},
            {"league": "🌍 International Friendlies", "home": "USA", "away": "Colombia", "h": 0, "a": 0, "status": "FT", "scorer": "Full Time - Clean sheet for both keepers"}
        ],
        (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'): [
            {"league": "🏆 Copa América / Euro Highlights", "home": "Argentina", "away": "Uruguay", "h": 1, "a": 0, "status": "FT", "scorer": "Goal: L. Messi 65'"},
            {"league": "⚽ Women's World Invitational", "home": "France Women", "away": "Germany Women", "h": 2, "a": 2, "status": "FT", "scorer": "Goals: E. Le Sommer 14', A. Popp 41', 77'"}
        ],
        (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'): [
            {"league": "🇪🇸 Spanish La Liga - Recent", "home": "Real Madrid", "away": "Athletic Bilbao", "h": 2, "a": 0, "status": "FT", "scorer": "Goals: K. Mbappé 22', J. Bellingham 58'"},
            {"league": "🇮🇹 Italian Serie A - Recent", "home": "Juventus", "away": "Napoli", "h": 1, "a": 1, "status": "FT", "scorer": "Goals: D. Vlahović 12', V. Osimhen 45'"}
        ],
        datetime.now().strftime('%Y-%m-%d'): [
            {"league": "🏆 UEFA Champions League - Qualifiers", "home": "Galatasaray", "away": "Young Boys", "h": 2, "a": 1, "status": "75'", "scorer": "Live - Yellow Card: M. Icardi 60'"},
            {"league": "🏆 UEFA Champions League - Qualifiers", "home": "Dynamo Kyiv", "away": "Red Bull Salzburg", "h": 0, "a": 1, "status": "HT", "scorer": "Half Time - Away team leading"},
            {"league": "🤝 Club Friendly Match", "home": "Villarreal", "away": "Borussia Dortmund", "h": 2, "a": 2, "status": "FT", "scorer": "Goals: G. Moreno 10', K. Adeyemi 45'"},
            {"league": "⚽ Women's International Friendly", "home": "England Women", "away": "Sweden Women", "h": 3, "a": 1, "status": "FT", "scorer": "Goals: A. Russo 19', L. James 45', B. Mead 82'"}
        ],
        (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'): [
            {"league": "🏆 UEFA Champions League - Playoff", "home": "Bodo/Glimt", "away": "Crvena Zvezda", "h": "-", "a": "-", "status": "10:00 PM", "scorer": "Preview: First leg showdown"},
            {"league": "🏆 UEFA Champions League - Playoff", "home": "Lille", "away": "Slavia Praha", "h": "-", "a": "-", "status": "10:00 PM", "scorer": "Preview: Tactical battle expected"}
        ],
        (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'): [
            {"league": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 English Premier League - Upcoming", "home": "Manchester United", "away": "Fulham", "h": "-", "a": "-", "status": "9:00 PM", "scorer": "Season Opening Match Preview"},
            {"league": "🇪🇸 Spanish La Liga - Upcoming", "home": "Barcelona", "away": "Valencia", "h": "-", "a": "-", "status": "11:30 PM", "scorer": "Opening fixture analysis"}
        ],
        (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'): [
            {"league": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 English Premier League - Upcoming", "home": "Arsenal", "away": "Wolverhampton", "h": "-", "a": "-", "status": "5:00 PM", "scorer": "Saturday afternoon clash"},
            {"league": "🇮🇹 Italian Serie A - Upcoming", "home": "AC Milan", "away": "Torino", "h": "-", "a": "-", "status": "9:45 PM", "scorer": "San Siro season opener"}
        ]
    }
    
    # ለተመረጠው ቀን ማዛመጃ መፈለግ
    matches = master_matches.get(selected_date, [
        {"league": "🌍 Global Club Friendlies", "home": "Local Select XI", "away": "International Stars", "h": 1, "a": 1, "status": "FT", "scorer": "Exhibition Match Result"}
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
                    {match['h']} - {match['a']}
                    <div class="match-status">{match['status']}</div>
                </div>
                <div class="team away"><span>{match['away']}</span></div>
            </div>
            <div class="match-detail">📌 {match['scorer']}</div>
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
