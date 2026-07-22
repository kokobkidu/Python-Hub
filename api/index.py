from flask import Flask, render_template_string, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

API_KEY = "276477041ca34aa6924720392f56415d"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_KEY}

@app.route('/')
def home():
    # ነባሪ ቀን ዛሬ እንዲሆን ማድረግ
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    match_id = request.args.get('match_id')
    
    # የሳምንቱን ቀናት ማዘጋጀት (ትናንት፣ ዛሬ፣ ነገ...)
    dates_list = []
    base_date = datetime.now() - timedelta(days=2)
    for i in range(6):
        d = base_date + timedelta(days=i)
        d_str = d.strftime('%Y-%m-%d')
        d_label = d.strftime('%a %d %b')
        dates_list.append({'date': d_str, 'label': d_label})
    
    matches = []
    try:
        url = f"{BASE_URL}/matches?date={selected_date}"
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            data = response.json()
            for m in data.get('matches', []):
                competition_name = m.get('competition', {}).get('name', 'Football Match')
                area_name = m.get('competition', {}).get('area', {}).get('name', '')
                league_display = f"{area_name} - {competition_name}" if area_name else competition_name
                
                home_team = m.get('homeTeam', {}).get('name', 'Home')
                away_team = m.get('awayTeam', {}).get('name', 'Away')
                
                score_info = m.get('score', {}).get('fullTime', {})
                h_goals = score_info.get('home')
                a_goals = score_info.get('away')
                
                status = m.get('status', 'SCHEDULED')
                
                matches.append({
                    "id": str(m.get('id')),
                    "league": league_display,
                    "home": home_team,
                    "away": away_team,
                    "h": h_goals if h_goals is not None else "-",
                    "a": a_goals if a_goals is not None else "-",
                    "status": status,
                    "utcDate": m.get('utcDate', '')
                })
    except Exception as e:
        print("API Error:", e)
        
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Koki Score</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 0; }}
            .top-bar {{ background-color: #2e7d32; color: white; padding: 12px; text-align: center; font-size: 19px; font-weight: bold; }}
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
            .score-box {{ width: 24%; text-align: center; background: #e8f5e9; padding: 6px; border-radius: 4px; font-weight: bold; font-size: 14px; color: #2e7d32; border: 1px solid #c8e6c9; text-decoration: none; display: block; }}
            .match-status {{ font-size: 9px; color: #666; margin-top: 3px; text-transform: uppercase; }}
            .no-match {{ text-align: center; padding: 30px; color: #666; font-weight: bold; background: white; border-radius: 8px; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="top-bar">⚽ Koki Score (Live API)</div>
        <div class="date-tabs">
    """
    
    for d in dates_list:
        is_active = "active" if d['date'] == selected_date else ""
        html_content += f'<a href="/?date={d["date"]}" class="date-tab {is_active}">{d["label"]}</a>'
        
    html_content += """
        </div>
        <div class="container">
    """
    
    if matches:
        current_league = ""
        for match in matches:
            if match['league'] != current_league:
                current_league = match['league']
                html_content += f'<div class="league-title">{current_league}</div>'
                
            html_content += f"""
            <div class="match-card">
                <div class="team home"><span>{match['home']}</span></div>
                <a href="/?date={selected_date}&match_id={match['id']}" class="score-box">
                    {match['h']} - {match['a']}
                    <div class="match-status">{match['status']}</div>
                </a>
                <div class="team away"><span>{match['away']}</span></div>
            </div>
            """
    else:
        html_content += f'<div class="no-match">No matches scheduled or available for this date ({selected_date}) on free API tier.</div>'
        
    html_content += """
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    app.run()
