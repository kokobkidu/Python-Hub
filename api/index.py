# የተስፋፋ የሊጎች ዝርዝር (Europe, Saudi, Brazil, MLS, etc.)
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

@app.route('/topscorers')
def topscorers():
    league_code = request.args.get('league', 'eng.1')
    scorers_data = []
    
    try:
        # 1. First attempt: Standard Leaders API
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
                for idx, leader in enumerate(leaders, start=1):
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
                    
        # 2. Fallback attempt if leaders list is empty (Fetch from Standings or Statistics if available)
        if not scorers_data:
            stat_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/statistics"
            s_res = requests.get(stat_url, timeout=5)
            if s_res.status_code == 200:
                s_data = s_res.json()
                stats_categories = s_data.get('stats', {}).get('categories', [])
                goals_stat = next((sc for sc in stats_categories if sc.get('name') == 'offense' or sc.get('name') == 'goals'), None)
                if goals_stat:
                    for idx, athlete_stat in enumerate(goals_stat.get('athletes', [])[:15], start=1):
                        ath = athlete_stat.get('athlete', {})
                        scorers_data.append({
                            "rank": idx,
                            "name": ath.get('displayName', 'Player'),
                            "team": ath.get('team', {}).get('displayName', ''),
                            "headshot": ath.get('headshot', ''),
                            "goals": int(athlete_stat.get('value', 0))
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
                    No top scorers data currently available for this league (Season break or pending data).
                </div>
            {% endif %}
        </div>
    </body>
    </html>
    """, scorers=scorers_data, leagues=LEAGUES_MAP, selected_league=league_code)
