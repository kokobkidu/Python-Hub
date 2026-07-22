from flask import Flask, render_template_string, request
from datetime import datetime, timedelta
import requests

app = Flask(__name__)

@app.route('/')
def home():
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    match_id = request.args.get('match_id')
    
    dates_list = []
    base_date = datetime.now() - timedelta(days=3)
    for i in range(7):
        d = base_date + timedelta(days=i)
        d_str = d.strftime('%Y-%m-%d')
        d_label = d.strftime('%a %d %b')
        dates_list.append({'date': d_str, 'label': d_label})
    
    matches = []
    try:
        live_api_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/all/scoreboard?dates={selected_date.replace('-', '')}"
        response = requests.get(live_api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            events = data.get('events', [])
            for ev in events:
                m_id = ev.get('id', '')
                comp_name = ev.get('season', {}).get('slug', 'Football League').upper()
                competitions = ev.get('competitions', [])
                for comp in competitions:
                    competitors = comp.get('competitors', [])
                    home_team, away_team, h_score, a_score = "Home", "Away", "-", "-"
                    for team in competitors:
                        if team.get('homeAway') == 'home':
                            home_team = team.get('team', {}).get('displayName', 'Home')
                            h_score = team.get('score', '-')
                        else:
                            away_team = team.get('team', {}).get('displayName', 'Away')
                            a_score = team.get('score', '-')
                    
                    status_type = comp.get('status', {}).get('type', {}).get('name', '')
                    status_detail = comp.get('status', {}).get('type', {}).get('shortDetail', 'TIMED')
                    
                    if status_type == 'STATUS_IN_PROGRESS':
                        clock = comp.get('status', {}).get('displayClock', '')
                        status_detail = f"{clock}' LIVE" if clock else "LIVE"
                    elif status_type == 'STATUS_SCHEDULED':
                        match_date_str = ev.get('date', '')
                        if match_date_str:
                            dt_obj = datetime.strptime(match_date_str, "%Y-%m-%dT%H:%MZ")
                            status_detail = dt_obj.strftime('%H:%M')
                    elif status_type == 'STATUS_FINAL':
                        status_detail = "FT"
                    
                    matches.append({
                        "id": m_id,
                        "league": comp_name,
                        "home": home_team,
                        "away": away_team,
                        "h": h_score,
                        "a": a_score,
                        "status": status_detail
                    })
    except Exception as e:
        print("API Error:", e)

    if match_id:
        selected_match = next((m for m in matches if m['id'] == match_id), None)
        if selected_match:
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Match Details</title>
                <style>
                    body { font-family: sans-serif; background: #f0f2f5; margin: 0; padding: 0; }
                    .top-bar { background: #1b5e20; color: white; padding: 14px; text-align: center; font-size: 18px; font-weight: bold; }
                    .back-btn { display: inline-block; margin: 15px; color: #1b5e20; text-decoration: none; font-weight: bold; }
                    .container { padding: 15px; max-width: 600px; margin: auto; background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
                    .score-header { text-align: center; font-size: 20px; font-weight: bold; color: #1b5e20; margin: 20px 0; background: #e8f5e9; padding: 15px; border-radius: 6px; }
                    .info-text { text-align: center; color: #555; font-size: 14px; margin-top: 15px; background: #f8f9fa; padding: 10px; border-radius: 6px; }
                </style>
            </head>
            <body>
                <div class="top-bar">⚽ Koki Score - Detail</div>
                <div style="max-width: 600px; margin: auto;"><a href="/?date={{ date }}" class="back-btn">⬅ Back</a></div>
                <div class="container">
                    <h3>{{ match.league }}</h3>
                    <div class="score-header">
                        {{ match.home }} {{ match.h }} - {{ match.a }} {{ match.away }}
                        <div style="font-size: 12px; color: #d32f2f; margin-top: 5px;">Status: {{ match.status }}</div>
                    </div>
                    <div class="info-text">
                        Official match result: <b>{{ match.home }} {{ match.h }}</b> and <b>{{ match.away }} {{ match.a }}</b>.
                    </div>
                </div>
            </body>
            </html>
            """, match=selected_match, date=selected_date)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Koki Score</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f8f9fa; margin: 0; padding: 0; }}
            .top-bar {{ background-color: #1b5e20; color: white; padding: 14px; text-align: center; font-size: 18px; font-weight: bold; }}
            .date-tabs {{ display: flex; background-color: #2e7d32; overflow-x: auto; white-space: nowrap; scrollbar-width: none; padding: 0 5px; }}
            .date-tabs::-webkit-scrollbar {{ display: none; }}
            .date-tab {{ color: #c8e6c9; padding: 12px 18px; text-decoration: none; font-size: 13px; font-weight: bold; text-align: center; display: inline-block; border-bottom: 3px solid transparent; }}
            .date-tab.active {{ color: white; border-bottom: 3px solid #ffeb3b; background-color: rgba(0,0,0,0.1); }}
            .container {{ padding: 12px; max-width: 600px; margin: auto; }}
            .league-title {{ font-size: 11px; font-weight: bold; color: #444; margin: 16px 4px 6px 4px; text-transform: uppercase; background: #e9ecef; padding: 6px 10px; border-radius: 4px; border-left: 4px solid #2e7d32; }}
            .match-card {{ background: white; margin-bottom: 8px; padding: 12px 8px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center; }}
            .team {{ width: 38%; font-weight: 600; font-size: 13px; color: #212529; display: flex; align-items: center; }}
            .team.home {{ justify-content: flex-end; text-align: right; }}
            .team.away {{ justify-content: flex-start; text-align: left; }}
            .score-box {{ width: 24%; text-align: center; background: #f1f8e9; padding: 6px 4px; border-radius: 6px; font-weight: bold; font-size: 14px; color: #2e7d32; border: 1px solid #dcedc8; text-decoration: none; display: block; }}
            .match-status {{ font-size: 10px; color: #d32f2f; margin-top: 2px; text-transform: uppercase; font-weight: bold; }}
            .no-match {{ text-align: center; padding: 40px 20px; color: #6c757d; font-weight: 500; background: white; border-radius: 8px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="top-bar">⚽ Koki Score ({selected_date})</div>
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
        html_content += f'<div class="no-match">No matches found for ({selected_date}).</div>'
        
    html_content += """
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    app.run()
