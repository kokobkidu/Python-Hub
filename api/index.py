
from flask import Flask, render_template_string, request
from datetime import datetime, timedelta
import urllib.request
import json

app = Flask(__name__)

@app.route('/')
def home():
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # የ7 ቀናት ማጣሪያ (Besoccer style)
    dates_list = []
    base_date = datetime.now() - timedelta(days=3)
    for i in range(7):
        d = base_date + timedelta(days=i)
        d_str = d.strftime('%Y-%m-%d')
        d_label = d.strftime('%a %d %b')
        dates_list.append({'date': d_str, 'label': d_label})
    
    matches = []
    error_msg = None
    
    try:
        # እውነተኛውን ነፃ የفوټبال API (Public football-data endpoint) በመጠቀም እውነተኛ ግጥሚያዎችን ማምጣት
        api_url = f"https://api.football-data.org/v4/matches?dateFrom={selected_date}&dateTo={selected_date}"
        req = urllib.request.Request(
            api_url, 
            headers={'X-Auth-Token': '32074f63c5d84a7e9375ffea8f467ea5'} # ነፃ እውነተኛ ቶከን
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            raw_matches = data.get('matches', [])
            
            for m in raw_matches:
                competition = m.get('competition', {}).get('name', 'International Match')
                home_team = m.get('homeTeam', {}).get('name', 'Home Team')
                away_team = m.get('awayTeam', {}).get('name', 'Away Team')
                score = m.get('score', {}).get('fullTime', {})
                h_goals = score.get('home')
                a_goals = score.get('away')
                status = m.get('status', 'SCHEDULED')
                
                matches.append({
                    "league": competition,
                    "home": home_team,
                    "away": away_team,
                    "h": h_goals if h_goals is not None else "-",
                    "a": a_goals if a_goals is not None else "-",
                    "status": "FT" if status == "FINISHED" else (status if status != "SCHEDULED" else m.get('utcDate', '')[11:16])
                })
    except Exception as e:
        error_msg = "እውነተኛውን ሰርቨር ማግኘት አልተቻለም። እባክዎ የኢንተርኔት ግንኙነትዎን ይፈትሹ።"

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
            .no-match {{ text-align: center; padding: 30px; color: #666; font-weight: bold; background: white; border-radius: 8px; margin-top: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
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
    
    if error_msg:
        html_content += f'<div class="no-match">{error_msg}</div>'
    elif matches:
        current_league = ""
        for match in matches:
            if match['league'] != current_league:
                current_league = match['league']
                html_content += f'<div class="league-title">🏆 {current_league}</div>'
                
            html_content += f"""
            <div class="match-card">
                <div class="team home"><span>{match['home']}</span></div>
                <div class="score-box">
                    {match['h']} - {match['a']}
                    <div class="match-status">{match['status']}</div>
                </div>
                <div class="team away"><span>{match['away']}</span></div>
            </div>
            """
    else:
        html_content += f'<div class="no-match">ለተመረጠው ቀን ({selected_date}) ከእውነተኛው የዓለም እግር ኳስ ሰርቨር የተመዘገበ ጨዋታ የለም።</div>'
        
    html_content += """
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    app.run()
