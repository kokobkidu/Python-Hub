from flask import Flask, render_template_string, request
from datetime import datetime, timedelta
import requests
import os

app = Flask(__name__)

# ቁልፍ ቃላት
ALLOWED_KEYWORDS = [
    "PREMIER LEAGUE", "ETHIOPIAN", "SERIE A", "BUNDESLIGA", 
    "LIGUE 1", "LALIGA", "LA LIGA", "CHAMPIONS LEAGUE", 
    "SUPER LIG", "PRO LEAGUE", "WORLD CUP", "MLS", "ARGENTINA"
]

# የሊጎች ዝርዝር
LEAGUES_MAP = {
    "eng.1": "English Premier League",
    "esp.1": "Spanish La Liga",
    "ita.1": "Italian Serie A",
    "ger.1": "German Bundesliga",
    "fra.1": "French Ligue 1"
}

@app.route('/')
def home():
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    match_id = request.args.get('match_id')
    
    dates_list = []
    base_date = datetime.now() - timedelta(days=3)
    for i in range(7):
        d = base_date + timedelta(days=i)
        dates_list.append({'date': d.strftime('%Y-%m-%d'), 'label': d.strftime('%a %d %b')})
    
    matches = []
    try:
        live_api_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/all/scoreboard?dates={selected_date.replace('-', '')}"
        response = requests.get(live_api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            for ev in data.get('events', []):
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
                
                comp_name = str(comp_name).upper()

                if not any(keyword in comp_name for keyword in ALLOWED_KEYWORDS):
                    continue

                for comp in ev.get('competitions', []):
                    home_team, away_team, h_score, a_score = "Home", "Away", "-", "-"
                    for team in comp.get('competitors', []):
                        if team.get('homeAway') == 'home':
                            home_team = team.get('team', {}).get('displayName', 'Home')
                            h_score = team.get('score', '-')
                        else:
                            away_team = team.get('team', {}).get('displayName', 'Away')
                            a_score = team.get('score', '-')
                    
                    if home_team in ["Home", "Away"] or away_team in ["Home", "Away"]:
                        continue

                    status_type = comp.get('status', {}).get('type', {}).get('name', '')
                    status_detail = comp.get('status', {}).get('type', {}).get('shortDetail', 'TIMED')
                    
                    if status_type == 'STATUS_IN_PROGRESS':
                        clock = comp.get('status', {}).get('displayClock', '')
                        status_detail = f"{clock}' LIVE" if clock else "LIVE"
                    elif status_type == 'STATUS_SCHEDULED':
                        h_score, a_score = "-", "-"
                        match_date_str = ev.get('date', '')
                        if match_date_str:
                            try:
                                dt_obj = datetime.strptime(match_date_str, "%Y-%m-%dT%H:%MZ") + timedelta(hours=3)
                                status_detail = dt_obj.strftime('%H:%M')
                            except:
                                pass
                    elif status_type == 'STATUS_FINAL':
                        status_detail = "FT"
                    
                    matches.append({
                        "id": m_id, "league": comp_name, "home": home_team, 
                        "away": away_team, "h": h_score, "a": a_score, "status": status_detail
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
                for item in det_data.get('details', []):
                    if item.get('text'):
                        match_details["events_list"].append({
                            "text": item.get('text', ''),
                            "clock": item.get('clock', {}).get('displayValue', ''),
                            "team": item.get('team', {}).get('displayName', '')
                        })
                
                boxscore = det_data.get('boxscore', {}).get('teams', [])
                if len(boxscore) >= 2:
                    home_stats = {st.get('label'): st.get('displayValue', '0') for st in boxscore[0].get('statistics', [])}
                    away_stats = {st.get('label'): st.get('displayValue', '0') for st in boxscore[1].get('statistics', [])}
                    for label in set(home_stats.keys()).union(set(away_stats.keys())):
                        h_val, a_val = home_stats.get(label, '0'), away_stats.get(label, '0')
                        if h_val != '0' or a_val != '0':
                            match_details["statistics"].append({"label": label, "home": h_val, "away": a_val})
        except Exception as err:
            print("Detail API Error:", err)

        if selected_match:
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{{ match.home }} vs {{ match.away }} - Koki Score</title>
                <script type="text/javascript" src="https://pl30518340.effectivecpmnetwork.com/8c/d4/6b/8cd46b5b8dc5c8760a2063e5f3663df5.js"></script>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f9; margin: 0; padding: 0; }
                    .top-bar { background: #0d47a1; color: white; padding: 14px; text-align: center; font-size: 18px; font-weight: bold; }
                    .nav-menu { display: flex; justify-content: center; background: #0a3578; padding: 8px; flex-wrap: wrap; }
                    .nav-link { color: white; text-decoration: none; font-weight: bold; margin: 4px 8px; font-size: 13px; }
                    .back-btn { display: inline-block; margin: 12px 15px; color: #0d47a1; text-decoration: none; font-weight: bold; font-size: 14px; }
                    .container { padding: 0 15px 20px 15px; max-width: 600px; margin: auto; }
                    .match-header-card { background: white; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
                    .league-badge { font-size: 11px; font-weight: bold; color: #1565c0; background: #e3f2fd; padding: 4px 10px; border-radius: 20px; display: inline-block; }
                    .teams-score { display: flex; justify-content: space-between; align-items: center; font-size: 16px; font-weight: bold; margin: 15px 0; }
                    .team-name { width: 38%; text-align: center; }
                    .score-badge { background: #0d47a1; color: white; padding: 8px 16px; border-radius: 8px; font-size: 20px; }
                    .card-box { background: white; border-radius: 12px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
                    .section-title { font-size: 13px; font-weight: bold; color: #555; margin-bottom: 15px; border-left: 4px solid #0d47a1; padding-left: 8px; }
                    .event-row { display: flex; align-items: center; font-size: 13px; padding: 8px 0; border-bottom: 1px solid #f1f1f1; }
                    .event-time { font-weight: bold; color: #0d47a1; width: 45px; }
                    .stat-info { display: flex; justify-content: space-between; font-size: 12px; font-weight: bold; margin-bottom: 6px; }
                    .no-data { text-align: center; color: #888; font-size: 13px; padding: 15px 0; }
                </style>
            </head>
            <body>
                <div class="top-bar">⚽ Koki Score Hub</div>
                <div class="nav-menu">
                    <a href="/" class="nav-link">🏟️ Matches</a>
                    <a href="/standings" class="nav-link">📊 Standings</a>
                    <a href="/topscorers" class="nav-link">⚽ Top Scorers</a>
                </div>
                <div style="max-width: 600px; margin: auto;"><a href="/?date={{ date }}" class="back-btn">⬅ Back to Matches</a></div>
                <div class="container">
                    <div class="match-header-card">
                        <div class="league-badge">{{ match.league }}</div>
                        <div class="teams-score">
                            <div class="team-name">{{ match.home }}</div>
                            <div class="score-badge">{{ match.h }} - {{ match.a }}</div>
                            <div class="team-name">{{ match.away }}</div>
                        </div>
                        <div style="font-size: 11px; color: #d32f2f; font-weight: bold;">Status: {{ match.status }}</div>
                    </div>
                    <div class="card-box">
                        <div class="section-title">⚽ Goals & Events</div>
                        {% if details.events_list %}
                            {% for ev in details.events_list %}
                                <div class="event-row">
                                    <div class="event-time">{{ ev.clock }}'</div>
                                    <div style="flex-grow: 1;">{{ ev.text }}</div>
                                    <div style="font-size: 11px; color: #666; font-weight: bold;">{{ ev.team }}</div>
                                </div>
                            {% endfor %}
                        {% else %}
                            <div class="no-data">No goals recorded yet.</div>
                        {% endif %}
                    </div>
                    <div class="card-box">
                        <div class="section-title">📊 Match Stats</div>
                        {% if details.statistics %}
                            {% for st in details.statistics %}
                                <div class="stat-info">
                                    <span>{{ st.home }}</span>
                                    <span style="color: #666; font-size: 11px;">{{ st.label }}</span>
                                    <span>{{ st.away }}</span>
                                </div>
                            {% endfor %}
                        {% else %}
                            <div class="no-data">No statistics available.</div>
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
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Koki Score</title>
        <script type="text/javascript" src="https://pl30518340.effectivecpmnetwork.com/8c/d4/6b/8cd46b5b8dc5c8760a2063e5f3663df5.js"></script>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f4f6f9; margin: 0; padding: 0; }}
            .top-bar {{ background-color: #0d47a1; color: white; padding: 14px; text-align: center; font-size: 18px; font-weight: bold; }}
            .nav-menu {{ display: flex; justify-content: center; background-color: #0a3578; padding: 8px; flex-wrap: wrap; }}
            .nav-link {{ color: white; text-decoration: none; font-weight: bold; margin: 4px 8px; font-size: 13px; opacity: 0.9; }}
            .nav-link.active {{ border-bottom: 2px solid #ffeb3b; color: #ffeb3b; }}
            .date-tabs {{ display: flex; background-color: #1565c0; overflow-x: auto; white-space: nowrap; scrollbar-width: none; padding: 0 5px; }}
            .date-tabs::-webkit-scrollbar {{ display: none; }}
            .date-tab {{ color: #bbdefb; padding: 12px 18px; text-decoration: none; font-size: 13px; font-weight: bold; display: inline-block; }}
            .date-tab.active {{ color: white; border-bottom: 3px solid #ffeb3b; background-color: rgba(0,0,0,0.1); }}
            .container {{ padding: 12px; max-width: 600px; margin: auto; }}
            .league-title {{ font-size: 11px; font-weight: bold; color: #444; margin: 16px 4px 6px 4px; text-transform: uppercase; background: #e9ecef; padding: 6px 10px; border-radius: 6px; border-left: 4px solid #1565c0; }}
            .match-card {{ background: white; margin-bottom: 8px; padding: 14px 10px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); display: flex; justify-content: space-between; align-items: center; }}
            .team {{ width: 38%; font-weight: 600; font-size: 13px; color: #212529; display: flex; align-items: center; }}
            .team.home {{ justify-content: flex-end; text-align: right; }}
            .team.away {{ justify-content: flex-start; text-align: left; }}
            .score-box {{ width: 26%; text-align: center; background: #e3f2fd; padding: 6px 4px; border-radius: 8px; font-weight: bold; font-size: 14px; color: #0d47a1; border: 1px solid #bbdefb; text-decoration: none; }}
            .match-status {{ font-size: 10px; color: #d32f2f; margin-top: 2px; font-weight: bold; }}
            .no-match {{ text-align: center; padding: 40px 20px; color: #6c757d; background: white; border-radius: 10px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="top-bar">⚽ Koki Score</div>
        <div class="nav-menu">
            <a href="/" class="nav-link active">🏟️ Matches</a>
            <a href="/standings" class="nav-link">📊 Standings</a>
            <a href="/topscorers" class="nav-link">⚽ Top Scorers</a>
        </div>
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
        html_content += f'<div class="no-match">No active matches found for ({selected_date}).</div>'
        
    html_content += "</div></body></html>"
    return html_content


@app.route('/standings')
def standings():
    league_code = request.args.get('league', 'eng.1')
    table_data = []
    
    try:
        url = f"https://site.api.espn.com/apis/v2/sports/soccer/{league_code}/standings"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            
            entries = []
            if 'children' in data and len(data['children']) > 0:
                entries = data['children'][0].get('standings', {}).get('entries', [])
            elif 'standings' in data:
                entries = data.get('standings', {}).get('entries', [])
                
            for entry in entries:
                team_name = entry.get('team', {}).get('displayName', 'Team')
                logo = entry.get('team', {}).get('logos', [{}])[0].get('href', '')
                
                stats = {s.get('name'): s.get('value') for s in entry.get('stats', [])}
                
                table_data.append({
                    "team": team_name,
                    "logo": logo,
                    "p": int(float(stats.get('gamesPlayed', 0))),
                    "w": int(float(stats.get('wins', 0))),
                    "d": int(float(stats.get('ties', 0))),
                    "l": int(float(stats.get('losses', 0))),
                    "gf": int(float(stats.get('pointsFor', 0))),
                    "ga": int(float(stats.get('pointsAgainst', 0))),
                    "gd": int(float(stats.get('pointDifferential', 0))),
                    "pts": int(float(stats.get('points', 0)))
                })
                
            table_data.sort(key=lambda x: (x['pts'], x['gd'], x['gf']), reverse=True)
            
            for idx, item in enumerate(table_data, start=1):
                item['rank'] = idx

    except Exception as e:
        print("Standings Error:", e)

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>League Standings - Koki Score</title>
        <script type="text/javascript" src="https://pl30518340.effectivecpmnetwork.com/8c/d4/6b/8cd46b5b8dc5c8760a2063e5f3663df5.js"></script>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f9; margin: 0; padding: 0; }
            .top-bar { background: #0d47a1; color: white; padding: 14px; text-align: center; font-size: 18px; font-weight: bold; }
            .nav-menu { display: flex; justify-content: center; background: #0a3578; padding: 8px; flex-wrap: wrap; }
            .nav-link { color: white; text-decoration: none; font-weight: bold; margin: 4px 8px; font-size: 13px; opacity: 0.9; }
            .nav-link.active { border-bottom: 2px solid #ffeb3b; color: #ffeb3b; }
            .league-selector { display: flex; overflow-x: auto; background: #1565c0; padding: 8px; scrollbar-width: none; }
            .league-btn { color: #bbdefb; text-decoration: none; padding: 6px 12px; font-size: 12px; font-weight: bold; border-radius: 15px; white-space: nowrap; margin-right: 5px; }
            .league-btn.active { background: #ffeb3b; color: #0d47a1; }
            .container { padding: 10px 5px; max-width: 600px; margin: auto; }
            .table-card { background: white; border-radius: 10px; overflow-x: auto; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
            table { width: 100%; border-collapse: collapse; font-size: 12px; white-space: nowrap; }
            th { background: #f1f3f5; color: #444; padding: 8px 4px; text-align: center; font-size: 10px; text-transform: uppercase; }
            td { padding: 8px 4px; border-bottom: 1px solid #eee; text-align: center; }
            .team-td { text-align: left; display: flex; align-items: center; font-weight: 600; max-width: 130px; overflow: hidden; text-overflow: ellipsis; }
            .team-logo { width: 16px; height: 16px; margin-right: 6px; flex-shrink: 0; }
            .rank { font-weight: bold; color: #0d47a1; width: 20px; }
            .pts { font-weight: bold; color: #000; background: #e3f2fd; }
        </style>
    </head>
    <body>
        <div class="top-bar">⚽ League Standings</div>
        <div class="nav-menu">
            <a href="/" class="nav-link">🏟️ Matches</a>
            <a href="/standings" class="nav-link active">📊 Standings</a>
            <a href="/topscorers" class="nav-link">⚽ Top Scorers</a>
        </div>
        <div class="league-selector">
            {% for code, name in leagues.items() %}
                <a href="/standings?league={{ code }}" class="league-btn {% if code == selected_league %}active{% endif %}">{{ name }}</a>
            {% endfor %}
        </div>
        <div class="container">
            <div class="table-card">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th style="text-align: left;">Team</th>
                            <th>P</th>
                            <th>W</th>
                            <th>D</th>
                            <th>L</th>
                            <th>F</th>
                            <th>A</th>
                            <th>GD</th>
                            <th>PTS</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% if table %}
                            {% for row in table %}
                            <tr>
                                <td class="rank">{{ row.rank }}</td>
                                <td class="team-td">
                                    {% if row.logo %}<img src="{{ row.logo }}" class="team-logo">{% endif %}
                                    <span>{{ row.team }}</span>
                                </td>
                                <td>{{ row.p }}</td>
                                <td>{{ row.w }}</td>
                                <td>{{ row.d }}</td>
                                <td>{{ row.l }}</td>
                                <td>{{ row.gf }}</td>
                                <td>{{ row.ga }}</td>
                                <td>{% if row.gd > 0 %}+{{ row.gd }}{% else %}{{ row.gd }}{% endif %}</td>
                                <td class="pts">{{ row.pts }}</td>
                            </tr>
                            {% endfor %}
                        {% else %}
                            <tr><td colspan="10" style="padding: 20px; color: #777;">No standings available for this league.</td></tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """, table=table_data, leagues=LEAGUES_MAP, selected_league=league_code)


# -------------------------------------------------------------
# 🔥 ደረጃ 1፡ TOP SCORERS ROUTE (የከፍተኛ ጎል አገባቢዎች ሰንጠረዥ)
# -------------------------------------------------------------
@app.route('/topscorers')
def topscorers():
    league_code = request.args.get('league', 'eng.1')
    scorers_data = []
    
    try:
        url = f"https://site.api.espn.com/apis/v2/sports/soccer/{league_code}/leaders"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            categories = data.get('leaders', [])
            
            # ጎል የሚያስቆጥሩትን Category መፈለግ (Goals)
            goals_category = next((c for c in categories if c.get('name') == 'goals' or c.get('displayName') == 'Goals'), None)
            if not goals_category and len(categories) > 0:
                goals_category = categories[0]
                
            if goals_category:
                leaders = goals_category.get('leaders', [])
                for idx, leader in enumerate(leaders, start=1):
                    athlete = leader.get('athlete', {})
                    name = athlete.get('displayName', 'Player')
                    headshot = athlete.get('headshot', '')
                    team = athlete.get('team', {}).get('displayName', '')
                    goals = leader.get('value', 0)
                    
                    scorers_data.append({
                        "rank": idx,
                        "name": name,
                        "team": team,
                        "headshot": headshot,
                        "goals": int(goals)
                    })
    except Exception as e:
        print("Top Scorers Error:", e)

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Top Scorers - Koki Score</title>
        <script type="text/javascript" src="https://pl30518340.effectivecpmnetwork.com/8c/d4/6b/8cd46b5b8dc5c8760a2063e5f3663df5.js"></script>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f9; margin: 0; padding: 0; }
            .top-bar { background: #0d47a1; color: white; padding: 14px; text-align: center; font-size: 18px; font-weight: bold; }
            .nav-menu { display: flex; justify-content: center; background: #0a3578; padding: 8px; flex-wrap: wrap; }
            .nav-link { color: white; text-decoration: none; font-weight: bold; margin: 4px 8px; font-size: 13px; opacity: 0.9; }
            .nav-link.active { border-bottom: 2px solid #ffeb3b; color: #ffeb3b; }
            .league-selector { display: flex; overflow-x: auto; background: #1565c0; padding: 8px; scrollbar-width: none; }
            .league-btn { color: #bbdefb; text-decoration: none; padding: 6px 12px; font-size: 12px; font-weight: bold; border-radius: 15px; white-space: nowrap; margin-right: 5px; }
            .league-btn.active { background: #ffeb3b; color: #0d47a1; }
            .container { padding: 10px; max-width: 600px; margin: auto; }
            .scorer-card { background: white; border-radius: 10px; padding: 10px 14px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 5px rgba(0,0,0,0.03); }
            .rank { font-size: 16px; font-weight: bold; color: #0d47a1; width: 25px; }
            .player-info { display: flex; align-items: center; flex-grow: 1; margin-left: 5px; }
            .player-img { width: 38px; height: 38px; border-radius: 50%; background: #eee; margin-right: 10px; object-fit: cover; }
            .player-name { font-size: 13px; font-weight: bold; color: #222; }
            .player-team { font-size: 11px; color: #666; }
            .goals-badge { background: #e3f2fd; color: #0d47a1; font-weight: bold; padding: 6px 12px; border-radius: 20px; font-size: 13px; }
        </style>
    </head>
    <body>
        <div class="top-bar">⚽ Top Scorers</div>
        <div class="nav-menu">
            <a href="/" class="nav-link">🏟️ Matches</a>
            <a href="/standings" class="nav-link">📊 Standings</a>
            <a href="/topscorers" class="nav-link active">⚽ Top Scorers</a>
        </div>
        <div class="league-selector">
            {% for code, name in leagues.items() %}
                <a href="/topscorers?league={{ code }}" class="league-btn {% if code == selected_league %}active{% endif %}">{{ name }}</a>
            {% endfor %}
        </div>
        <div class="container">
            {% if scorers %}
                {% for player in scorers %}
                <div class="scorer-card">
                    <div class="rank">#{{ player.rank }}</div>
                    <div class="player-info">
                        {% if player.headshot %}
                            <img src="{{ player.headshot }}" class="player-img" alt="">
                        {% else %}
                            <div class="player-img" style="display:flex;align-items:center;justify-content:center;font-size:18px;">👤</div>
                        {% endif %}
                        <div>
                            <div class="player-name">{{ player.name }}</div>
                            <div class="player-team">{{ player.team }}</div>
                        </div>
                    </div>
                    <div class="goals-badge">⚽ {{ player.goals }} Goals</div>
                </div>
                {% endfor %}
            {% else %}
                <div style="text-align:center; padding: 30px; color: #777; background: white; border-radius: 10px;">
                    No top scorers data available for this league currently.
                </div>
            {% endif %}
        </div>
    </body>
    </html>
    """, scorers=scorers_data, leagues=LEAGUES_MAP, selected_league=league_code)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
