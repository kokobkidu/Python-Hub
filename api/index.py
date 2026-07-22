from flask import Flask, render_template_string, request
from datetime import datetime, timedelta
import requests
import os

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
                
                comp_name = "FOOTBALL LEAGUE"
                try:
                    competition_data = ev.get('competitions', [])[0]
                    if 'tournament' in competition_data and competition_data['tournament'].get('name'):
                        comp_name = competition_data['tournament']['name']
                    elif 'season' in ev and isinstance(ev['season'], dict) and ev['season'].get('slug'):
                        comp_name = str(ev['season']['slug']).replace('-', ' ')
                    elif 'name' in competition_data:
                        comp_name = competition_data.get('name')
                    else:
                        comp_name = ev.get('name', 'Football League')
                except:
                    comp_name = "Football League"
                
                if not isinstance(comp_name, str):
                    comp_name = "Football League"
                
                comp_name = comp_name.upper()

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
                    
                    # የውሸት ወይም ያልታወቁ ቡድኖችን ማጣራት (Filter out mock/test entries)
                    if home_team in ["Home", "Away"] or away_team in ["Home", "Away"] or not home_team or not away_team:
                        continue

                    status_type = comp.get('status', {}).get('type', {}).get('name', '')
                    status_detail = comp.get('status', {}).get('type', {}).get('shortDetail', 'TIMED')
                    
                    if status_type == 'STATUS_IN_PROGRESS':
                        clock = comp.get('status', {}).get('displayClock', '')
                        status_detail = f"{clock}' LIVE" if clock else "LIVE"
                    elif status_type == 'STATUS_SCHEDULED':
                        h_score = "-"
                        a_score = "-"
                        match_date_str = ev.get('date', '')
                        if match_date_str:
                            try:
                                dt_obj = datetime.strptime(match_date_str, "%Y-%m-%dT%H:%MZ")
                                dt_obj = dt_obj + timedelta(hours=3)
                                status_detail = dt_obj.strftime('%H:%M')
                            except:
                                pass
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
        
        match_details = {"events_list": [], "statistics": []}
        try:
            detail_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/all/summary?event={match_id}"
            det_res = requests.get(detail_url, timeout=5)
            if det_res.status_code == 200:
                det_data = det_res.json()
                
                details_array = det_data.get('details', [])
                for item in details_array:
                    text = item.get('text', '')
                    clock = item.get('clock', {}).get('displayValue', '')
                    team_obj = item.get('team', {}).get('displayName', '')
                    if text:
                        match_details["events_list"].append({"text": text, "clock": clock, "team": team_obj})
                
                boxscore = det_data.get('boxscore', {}).get('teams', [])
                if len(boxscore) >= 2:
                    home_stats = {st.get('label'): st.get('displayValue', '0') for st in boxscore[0].get('statistics', [])}
                    away_stats = {st.get('label'): st.get('displayValue', '0') for st in boxscore[1].get('statistics', [])}
                    
                    all_labels = set(home_stats.keys()).union(set(away_stats.keys()))
                    for label in all_labels:
                        h_val = home_stats.get(label, '0')
                        a_val = away_stats.get(label, '0')
                        # ትክክለኛ ስታቲስቲክስ ከሌለ (ሁለቱም 0 ከሆኑ) አናሳይም
                        if h_val != '0' or a_val != '0':
                            match_details["statistics"].append({
                                "label": label,
                                "home": h_val,
                                "away": a_val
                            })
        except Exception as err:
            print("Detail API Error:", err)

        if selected_match:
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{{ match.home }} vs {{ match.away }} - Koki Score</title>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f9; margin: 0; padding: 0; }
                    .top-bar { background: #1b5e20; color: white; padding: 14px; text-align: center; font-size: 18px; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                    .back-btn { display: inline-block; margin: 12px 15px; color: #1b5e20; text-decoration: none; font-weight: bold; font-size: 14px; }
                    .container { padding: 0 15px 20px 15px; max-width: 600px; margin: auto; }
                    .match-header-card { background: white; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); padding: 20px; text-align: center; margin-bottom: 15px; }
                    .league-badge { font-size: 11px; font-weight: bold; color: #2e7d32; text-transform: uppercase; margin-bottom: 10px; background: #e8f5e9; display: inline-block; padding: 4px 10px; border-radius: 20px; }
                    .teams-score { display: flex; justify-content: space-between; align-items: center; font-size: 16px; font-weight: bold; color: #333; margin: 15px 0; }
                    .team-name { width: 38%; text-align: center; word-wrap: break-word; }
                    .score-badge { background: #1b5e20; color: white; padding: 8px 16px; border-radius: 8px; font-size: 20px; font-weight: bold; }
                    .status-badge { font-size: 11px; color: #d32f2f; text-transform: uppercase; font-weight: bold; margin-top: 8px; }
                    
                    .card-box { background: white; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); padding: 15px; margin-bottom: 15px; }
                    .section-title { font-size: 13px; font-weight: bold; color: #555; margin-bottom: 15px; text-transform: uppercase; border-left: 4px solid #1b5e20; padding-left: 8px; }
                    
                    .stat-row { margin-bottom: 12px; }
                    .stat-info { display: flex; justify-content: space-between; font-size: 12px; font-weight: bold; color: #333; margin-bottom: 4px; }
                    
                    .event-row { display: flex; align-items: center; font-size: 13px; padding: 8px 0; border-bottom: 1px solid #f1f1f1; color: #444; }
                    .event-time { font-weight: bold; color: #1b5e20; width: 45px; }
                    .no-data { text-align: center; color: #888; font-size: 13px; padding: 15px 0; }
                </style>
            </head>
            <body>
                <div class="top-bar">⚽ Koki Score Hub</div>
                <div style="max-width: 600px; margin: auto;"><a href="/?date={{ date }}" class="back-btn">⬅ Back to Matches</a></div>
                
                <div class="container">
                    <div class="match-header-card">
                        <div class="league-badge">{{ match.league }}</div>
                        <div class="teams-score">
                            <div class="team-name">{{ match.home }}</div>
                            <div class="score-badge">{{ match.h }} - {{ match.a }}</div>
                            <div class="team-name">{{ match.away }}</div>
                        </div>
                        <div class="status-badge">Status: {{ match.status }}</div>
                    </div>

                    <div class="card-box">
                        <div class="section-title">⚽ Goal Events & Timeline</div>
                        {% if details.events_list %}
                            {% for ev in details.events_list %}
                                <div class="event-row">
                                    <div class="event-time">{{ ev.clock }}'</div>
                                    <div style="flex-grow: 1;">{{ ev.text }}</div>
                                    <div style="font-size: 11px; color: #666; font-weight: bold;">{{ ev.team }}</div>
                                </div>
                            {% endfor %}
                        {% else %}
                            <div class="no-data">No match events or goals recorded for this game.</div>
                        {% endif %}
                    </div>

                    <div class="card-box">
                        <div class="section-title">📊 Match Statistics</div>
                        {% if details.statistics %}
                            {% for st in details.statistics %}
                                <div class="stat-row">
                                    <div class="stat-info">
                                        <span>{{ st.home }}</span>
                                        <span style="color: #666; text-transform: uppercase; font-size: 11px;">{{ st.label }}</span>
                                        <span>{{ st.away }}</span>
                                    </div>
                                </div>
                            {% endfor %}
                        {% else %}
                            <div class="no-data">Detailed statistics are not available for this match.</div>
                        {% endif %}
                    </div>
                </div>
            </body>
            </html>
            """, match=selected_match, date=selected_date, details=match_details)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Koki Score</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f4f6f9; margin: 0; padding: 0; }}
            .top-bar {{ background-color: #1b5e20; color: white; padding: 14px; text-align: center; font-size: 18px; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .date-tabs {{ display: flex; background-color: #2e7d32; overflow-x: auto; white-space: nowrap; scrollbar-width: none; padding: 0 5px; }}
            .date-tabs::-webkit-scrollbar {{ display: none; }}
            .date-tab {{ color: #c8e6c9; padding: 12px 18px; text-decoration: none; font-size: 13px; font-weight: bold; text-align: center; display: inline-block; border-bottom: 3px solid transparent; }}
            .date-tab.active {{ color: white; border-bottom: 3px solid #ffeb3b; background-color: rgba(0,0,0,0.1); }}
            .container {{ padding: 12px; max-width: 600px; margin: auto; }}
            .league-title {{ font-size: 11px; font-weight: bold; color: #444; margin: 16px 4px 6px 4px; text-transform: uppercase; background: #e9ecef; padding: 6px 10px; border-radius: 6px; border-left: 4px solid #2e7d32; }}
            .match-card {{ background: white; margin-bottom: 8px; padding: 14px 10px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); display: flex; justify-content: space-between; align-items: center; transition: transform 0.1s; }}
            .match-card:active {{ transform: scale(0.98); }}
            .team {{ width: 38%; font-weight: 600; font-size: 13px; color: #212529; display: flex; align-items: center; }}
            .team.home {{ justify-content: flex-end; text-align: right; }}
            .team.away {{ justify-content: flex-start; text-align: left; }}
            .score-box {{ width: 26%; text-align: center; background: #e8f5e9; padding: 6px 4px; border-radius: 8px; font-weight: bold; font-size: 14px; color: #1b5e20; border: 1px solid #c8e6c9; text-decoration: none; display: block; }}
            .match-status {{ font-size: 10px; color: #d32f2f; margin-top: 2px; text-transform: uppercase; font-weight: bold; }}
            .no-match {{ text-align: center; padding: 40px 20px; color: #6c757d; font-weight: 500; background: white; border-radius: 10px; margin-top: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); }}
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
        html_content += f'<div class="no-match">No matches found for ({selected_date}). Please try another date.</div>'
        
    html_content += """
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
