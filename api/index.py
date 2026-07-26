import os
import requests
from datetime import datetime
from flask import Flask, render_template_string, request

app = Flask(__name__)

LEAGUES_MAP = {
    "eng.1": "English Premier League",
    "esp.1": "Spanish La Liga",
    "ita.1": "Italian Serie A",
    "ger.1": "German Bundesliga",
    "fra.1": "French Ligue 1",
    "uefa.champions": "UEFA Champions League",
    "saudi.1": "Saudi Pro League",
    "bra.1": "Brazilian Série A",
    "usa.1": "MLS"
}

def extract_league_name(event):
    """ከ ESPN API የሊጉን ወይም የውድድሩን ትክክለኛ ስም ማውጫ"""
    # Option 1: competitions -> league -> name / abbreviation
    comps = event.get('competitions', [])
    if comps:
        lg = comps[0].get('league', {})
        if lg.get('name'):
            return lg.get('name')
        if lg.get('abbreviation'):
            return lg.get('abbreviation')

    # Option 2: Direct event -> league
    evt_lg = event.get('league', {})
    if evt_lg.get('name'):
        return evt_lg.get('name')
    if evt_lg.get('displayName'):
        return evt_lg.get('displayName')

    # Option 3: Season Slug
    season_slug = event.get('season', {}).get('slug', '')
    if season_slug:
        return season_slug.replace('-', ' ').title()

    return "Soccer Match"

@app.route('/')
def home():
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/all/scoreboard"
    if selected_date:
        url += f"?dates={selected_date.replace('-', '')}"
        
    matches = []
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            events = res.json().get('events', [])
            for event in events:
                comp = event['competitions'][0]
                home_team = comp['competitors'][0]
                away_team = comp['competitors'][1]
                
                status_state = event['status']['type']['state']
                detail = event['status']['type']['shortDetail']
                
                if status_state == 'in':
                    status = "LIVE"
                elif status_state == 'post':
                    status = "FINISHED"
                else:
                    status = "UPCOMING"

                # የሊጉን ስም በትክክል ማውጫ
                league_name = extract_league_name(event)

                matches.append({
                    "id": event.get('id'),
                    "league": league_name,
                    "home": home_team['team']['displayName'],
                    "home_logo": home_team['team'].get('logo', ''),
                    "home_score": home_team.get('score', '0'),
                    "away": away_team['team']['displayName'],
                    "away_logo": away_team['team'].get('logo', ''),
                    "away_score": away_team.get('score', '0'),
                    "status": status,
                    "detail": detail
                })
    except Exception as e:
        print("Error fetching matches:", e)

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Koki Score - Live Football</title>
        <script type="text/javascript" src="https://pl30518340.effectivecpmnetwork.com/8c/d4/6b/8cd46b5b8dc5c8760a2063e5f3663df5.js"></script>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f9; margin: 0; padding: 0; }
            .top-bar { background: #0d47a1; color: white; padding: 14px; text-align: center; font-size: 18px; font-weight: bold; }
            .nav-menu { display: flex; justify-content: center; background: #0a3578; padding: 8px; flex-wrap: wrap; }
            .nav-link { color: white; text-decoration: none; font-weight: bold; margin: 4px 8px; font-size: 13px; opacity: 0.9; }
            .nav-link.active { border-bottom: 2px solid #ffeb3b; color: #ffeb3b; }
            .date-picker { background: white; padding: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
            .date-picker input { padding: 8px 14px; border: 1px solid #ccc; border-radius: 6px; font-size: 14px; outline: none; font-weight: bold; color: #0d47a1; }
            .container { padding: 10px; max-width: 600px; margin: auto; }
            .match-card { background: white; border-radius: 10px; padding: 12px; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); display: block; text-decoration: none; color: inherit; }
            .league-title { font-size: 11px; font-weight: bold; color: #0d47a1; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f0f0f0; padding-bottom: 4px; }
            .match-header { font-size: 11px; color: #666; text-transform: uppercase; margin-bottom: 8px; font-weight: bold; display: flex; align-items: center; gap: 6px; }
            .teams { display: flex; justify-content: space-between; align-items: center; }
            .team { display: flex; align-items: center; width: 40%; }
            .team.away { justify-content: flex-end; }
            .logo { width: 24px; height: 24px; margin: 0 6px; object-fit: contain; }
            .score { font-size: 18px; font-weight: bold; background: #0d47a1; color: white; padding: 4px 10px; border-radius: 6px; }
            .badge { font-size: 10px; padding: 3px 6px; border-radius: 4px; font-weight: bold; display: inline-block; }
            .LIVE { background: #ffebee; color: #c62828; }
            .FINISHED { background: #e8f5e9; color: #2e7d32; }
            .UPCOMING { background: #e3f2fd; color: #1565c0; }
        </style>
    </head>
    <body>
        <div class="top-bar">⚽ Koki Score</div>
        <div class="nav-menu">
            <a href="/" class="nav-link active">🏟️ Matches</a>
            <a href="/standings" class="nav-link">📊 Standings</a>
            <a href="/topscorers" class="nav-link">⚽ Top Scorers</a>
        </div>
        <div class="date-picker">
            <form method="GET" action="/">
                <input type="date" name="date" value="{{ selected_date }}" onchange="this.form.submit()">
            </form>
        </div>
        <div class="container">
            {% for m in matches %}
            <a href="/match/{{ m.id }}" class="match-card">
                <div class="league-title">
                    <span>🏆 {{ m.league }}</span>
                    <span style="color: #666; font-weight: normal;">{{ m.detail }}</span>
                </div>
                <div class="match-header">
                    <span class="badge {{ m.status }}">{{ m.status }}</span>
                </div>
                <div class="teams">
                    <div class="team">
                        <img class="logo" src="{{ m.home_logo }}" onerror="this.style.display='none'">
                        <span>{{ m.home }}</span>
                    </div>
                    <div class="score">{{ m.home_score }} - {{ m.away_score }}</div>
                    <div class="team away">
                        <span>{{ m.away }}</span>
                        <img class="logo" src="{{ m.away_logo }}" onerror="this.style.display='none'">
                    </div>
                </div>
            </a>
            {% else %}
            <p style="text-align:center; color: #777; padding: 20px;">No matches found for the selected date.</p>
            {% endfor %}
        </div>
    </body>
    </html>
    """, matches=matches, selected_date=selected_date)


@app.route('/match/<match_id>')
def match_details(match_id):
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/all/summary?event={match_id}"
    match_data = {}
    events = []
    stats = []
    
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            header = data.get('header', {}).get('competitions', [{}])[0]
            home_team = header.get('competitors', [{}])[0]
            away_team = header.get('competitors', [{}])[1]
            
            league_name = data.get('header', {}).get('league', {}).get('name') or data.get('header', {}).get('league', {}).get('displayName', 'Football Match')

            match_data = {
                "league": league_name,
                "home": home_team.get('team', {}).get('displayName', 'Home'),
                "home_score": home_team.get('score', '0'),
                "away": away_team.get('team', {}).get('displayName', 'Away'),
                "away_score": away_team.get('score', '0'),
                "status": header.get('status', {}).get('type', {}).get('shortDetail', 'FT')
            }
            
            # Key Details & Timeline
            key_events = data.get('keyEvents', [])
            for k in key_events:
                events.append({
                    "time": k.get('clock', {}).get('displayValue', ''),
                    "text": k.get('text', ''),
                    "type": k.get('type', {}).get('text', '')
                })

            # Match Stats
            boxscore = data.get('boxscore', {}).get('teams', [])
            if len(boxscore) == 2:
                home_stats = {s['name']: s['displayValue'] for s in boxscore[0].get('statistics', [])}
                away_stats = {s['name']: s['displayValue'] for s in boxscore[1].get('statistics', [])}
                
                all_keys = set(home_stats.keys()).union(set(away_stats.keys()))
                for k in sorted(all_keys):
                    stats.append({
                        "name": k.replace('label', '').replace('%', ' %').upper(),
                        "home": home_stats.get(k, '-'),
                        "away": away_stats.get(k, '-')
                    })
    except Exception as e:
        print("Match detail error:", e)

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
            .container { padding: 12px; max-width: 600px; margin: auto; }
            .back-btn { display: inline-block; margin-bottom: 12px; color: #0d47a1; text-decoration: none; font-weight: bold; font-size: 14px; }
            .card { background: white; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); }
            .header-league { text-align: center; font-size: 11px; background: #e3f2fd; color: #0d47a1; font-weight: bold; padding: 4px 10px; border-radius: 12px; display: inline-block; margin: auto; }
            .score-box { display: flex; justify-content: space-around; align-items: center; margin-top: 15px; text-align: center; }
            .team-name { font-size: 16px; font-weight: bold; width: 35%; }
            .score-num { font-size: 24px; font-weight: bold; background: #0d47a1; color: white; padding: 6px 16px; border-radius: 8px; }
            .status-text { text-align: center; color: #c62828; font-size: 11px; font-weight: bold; margin-top: 8px; }
            .section-title { font-size: 13px; font-weight: bold; color: #0d47a1; margin-bottom: 10px; border-bottom: 2px solid #e3f2fd; padding-bottom: 4px; }
            .stat-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f0f0f0; font-size: 12px; }
            .stat-name { color: #555; font-weight: 500; }
        </style>
    </head>
    <body>
        <div class="top-bar">⚽ Koki Score Hub</div>
        <div class="container">
            <a href="/" class="back-btn">← Back to Matches</a>
            
            <div class="card" style="text-align: center;">
                <div class="header-league">🏆 {{ match.league }}</div>
                <div class="score-box">
                    <div class="team-name">{{ match.home }}</div>
                    <div class="score-num">{{ match.home_score }} - {{ match.away_score }}</div>
                    <div class="team-name">{{ match.away }}</div>
                </div>
                <div class="status-text">STATUS: {{ match.status }}</div>
            </div>

            <div class="card">
                <div class="section-title">⚽ GOAL EVENTS & TIMELINE</div>
                {% if events %}
                    {% for ev in events %}
                        <div style="font-size: 12px; padding: 4px 0;"><b>{{ ev.time }}</b> - {{ ev.text }}</div>
                    {% endfor %}
                {% else %}
                    <p style="font-size:12px; color: #777; text-align:center;">No match events or goals recorded for this game.</p>
                {% endif %}
            </div>

            <div class="card">
                <div class="section-title">📊 MATCH STATISTICS</div>
                {% if stats %}
                    {% for st in stats %}
                        <div class="stat-row">
                            <b>{{ st.home }}</b>
                            <span class="stat-name">{{ st.name }}</span>
                            <b>{{ st.away }}</b>
                        </div>
                    {% endfor %}
                {% else %}
                    <p style="font-size:12px; color: #777; text-align:center;">No detailed statistics available for this match.</p>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """, match=match_data, events=events, stats=stats)


@app.route('/standings')
def standings():
    league_code = request.args.get('league', 'eng.1')
    standings_data = []
    
    url = f"https://site.api.espn.com/apis/v2/sports/soccer/{league_code}/standings"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            entries = []
            
            if 'children' in data and len(data['children']) > 0:
                for child in data['children']:
                    if 'standings' in child and 'entries' in child['standings']:
                        entries.extend(child['standings']['entries'])
            elif 'standings' in data and 'entries' in data['standings']:
                entries = data['standings']['entries']
            
            for idx, item in enumerate(entries, start=1):
                team = item.get('team', {})
                stats_list = item.get('stats', [])
                stats = {s.get('name'): s.get('value') for s in stats_list if 'name' in s}
                
                rank_val = stats.get('rank', idx)
                if not rank_val:
                    rank_val = idx

                standings_data.append({
                    "rank": int(rank_val),
                    "team": team.get('displayName', 'Team'),
                    "logo": team.get('logos', [{}])[0].get('href', '') if team.get('logos') else '',
                    "played": int(stats.get('gamesPlayed', 0)),
                    "wins": int(stats.get('wins', 0)),
                    "draws": int(stats.get('ties', 0)),
                    "losses": int(stats.get('losses', 0)),
                    "gf": int(stats.get('pointsFor', 0)),
                    "ga": int(stats.get('pointsAgainst', 0)),
                    "gd": int(stats.get('pointDifferential', 0)),
                    "pts": int(stats.get('points', 0))
                })
                
            standings_data = sorted(standings_data, key=lambda x: x['rank'])
            
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
            .container { padding: 10px; max-width: 600px; margin: auto; }
            table { width: 100%; background: white; border-collapse: collapse; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.03); font-size: 12px; }
            th { background: #f0f4f8; color: #333; padding: 8px 4px; text-align: center; font-weight: bold; }
            td { padding: 8px 4px; text-align: center; border-bottom: 1px solid #eee; }
            .team-cell { display: flex; align-items: center; text-align: left; font-weight: bold; color: #111; }
            .team-logo { width: 18px; height: 18px; margin-right: 6px; object-fit: contain; }
            .pts-col { background: #e3f2fd; font-weight: bold; color: #0d47a1; }
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
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th style="text-align:left;">TEAM</th>
                        <th>P</th>
                        <th>W</th>
                        <th>D</th>
                        <th>L</th>
                        <th>F</th>
                        <th>A</th>
                        <th>GD</th>
                        <th class="pts-col">PTS</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in standings %}
                    <tr>
                        <td style="color:#0d47a1; font-weight:bold;">{{ row.rank }}</td>
                        <td class="team-cell">
                            {% if row.logo %}<img src="{{ row.logo }}" class="team-logo">{% endif %}
                            <span>{{ row.team }}</span>
                        </td>
                        <td>{{ row.played }}</td>
                        <td>{{ row.wins }}</td>
                        <td>{{ row.draws }}</td>
                        <td>{{ row.losses }}</td>
                        <td>{{ row.gf }}</td>
                        <td>{{ row.ga }}</td>
                        <td>{{ row.gd }}</td>
                        <td class="pts-col">{{ row.pts }}</td>
                    </tr>
                    {% else %}
                    <tr><td colspan="10">No standings data available currently.</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """, standings=standings_data, leagues=LEAGUES_MAP, selected_league=league_code)


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
            
            goals_category = next((c for c in categories if c.get('name') in ['goals', 'scoring'] or 'goal' in c.get('displayName', '').lower()), None)
            if not goals_category and len(categories) > 0:
                goals_category = categories[0]
                
            if goals_category:
                leaders = goals_category.get('leaders', [])
                for idx, leader in enumerate(leaders[:20], start=1):
                    athlete = leader.get('athlete', {})
                    name = athlete.get('displayName', athlete.get('fullName', 'Player'))
                    headshot = athlete.get('headshot', {}).get('href', '') if isinstance(athlete.get('headshot'), dict) else athlete.get('headshot', '')
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
                    No top scorers data currently available for this league.
                </div>
            {% endif %}
        </div>
    </body>
    </html>
    """, scorers=scorers_data, leagues=LEAGUES_MAP, selected_league=league_code)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
