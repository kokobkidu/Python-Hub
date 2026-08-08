import os
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, send_from_directory

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

# ---------------------------------------------------------
# ADSTERRA AD CODES SECTION
# ---------------------------------------------------------
SOCIAL_BAR_CODE = """
<script type="text/javascript" src="https://pl30518340.effectivecpmnetwork.com/8c/d4/6b/8cd46b5b8dc5c8760a2063e5f3663df5.js"></script>
"""

INTERSTITIAL_AD_CODE = """
<!-- Interstitial Ad Code -->
"""

BANNER_AD_CODE = """
<div style="text-align: center; margin: 15px 0; min-height: 50px;">
    <!-- Banner Ad Code Space -->
</div>
"""
# ---------------------------------------------------------

def extract_league_name(event):
    comps = event.get('competitions', [])
    if comps:
        lg = comps[0].get('league', {})
        if lg.get('displayName'):
            return lg.get('displayName')
        if lg.get('name'):
            return lg.get('name')

    evt_lg = event.get('league', {})
    if evt_lg.get('displayName'):
        return evt_lg.get('displayName')
    if evt_lg.get('name'):
        return evt_lg.get('name')

    season_slug = event.get('season', {}).get('slug', '')
    if season_slug:
        return season_slug.replace('-', ' ').title()

    return "Football Match"

def format_kickoff_time(date_str):
    if not date_str:
        return ""
    try:
        clean_date = date_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_date)
        eat_time = dt + timedelta(hours=3)
        return eat_time.strftime("%I:%M %p")
    except Exception:
        return ""

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('static', 'manifest.json')

# Route for Service Worker from root to grant full PWA scope
@app.route('/sw.js')
def serve_sw():
    response = send_from_directory('static', 'sw.js')
    response.headers['Service-Worker-Allowed'] = '/'
    return response

PWA_HEADER = """
        <link rel="manifest" href="/manifest.json">
        <meta name="theme-color" content="#0d47a1">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="apple-mobile-web-app-title" content="Koki Score">
        <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/5328/5328320.png">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
"""

PWA_SCRIPT = """
    <script>
      if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
          navigator.serviceWorker.register('/sw.js', {scope: '/'}).then(function(reg) {
            console.log('ServiceWorker registered:', reg);
          }).catch(function(err) {
            console.log('ServiceWorker registration failed:', err);
          });
        });
      }
      function toggleMenu() {
        var menu = document.getElementById('sideMenu');
        var overlay = document.getElementById('menuOverlay');
        if (menu.style.left === '0px') {
            menu.style.left = '-280px';
            overlay.style.display = 'none';
        } else {
            menu.style.left = '0px';
            overlay.style.display = 'block';
        }
      }
      // Auto-refresh match data every 60 seconds
      if (window.location.pathname === '/' || window.location.pathname.startsWith('/match/')) {
          setInterval(function() {
              window.location.reload();
          }, 60000);
      }
    </script>
"""

COMMON_STYLE = """
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f9; margin: 0; padding: 0; padding-bottom: 65px; }
    .top-bar { background: #0d47a1; color: white; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; font-size: 18px; font-weight: bold; position: sticky; top: 0; z-index: 100; }
    .top-bar .icon-btn { color: white; font-size: 18px; text-decoration: none; cursor: pointer; background: none; border: none; }
    .nav-menu { display: flex; justify-content: center; background: #0a3578; padding: 8px; flex-wrap: wrap; }
    .nav-link { color: white; text-decoration: none; font-weight: bold; margin: 4px 8px; font-size: 13px; opacity: 0.9; }
    .nav-link.active { border-bottom: 2px solid #ffeb3b; color: #ffeb3b; }
    .container { padding: 10px; max-width: 600px; margin: auto; }
    
    /* Side Menu */
    .side-menu { position: fixed; top: 0; left: -280px; width: 260px; height: 100%; background: white; box-shadow: 2px 0 10px rgba(0,0,0,0.2); z-index: 1000; transition: left 0.3s ease; overflow-y: auto; }
    .menu-header { background: #0d47a1; color: white; padding: 20px 15px; display: flex; align-items: center; gap: 12px; }
    .menu-header i { font-size: 32px; }
    .menu-item { display: flex; align-items: center; gap: 15px; padding: 14px 20px; color: #333; text-decoration: none; font-size: 14px; border-bottom: 1px solid #f0f0f0; }
    .menu-item i { color: #0d47a1; width: 20px; text-align: center; }
    .menu-divider { padding: 10px 20px 4px 20px; font-size: 11px; font-weight: bold; color: #888; text-transform: uppercase; background: #f8f9fa; }
    .menu-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 999; display: none; }

    /* Bottom Navigation Bar */
    .bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; background: white; border-top: 1px solid #ddd; display: flex; justify-content: space-around; padding: 6px 0; z-index: 100; box-shadow: 0 -2px 5px rgba(0,0,0,0.05); }
    .nav-item { text-align: center; color: #777; text-decoration: none; font-size: 10px; font-weight: bold; flex: 1; display: flex; flex-direction: column; align-items: center; }
    .nav-item i { font-size: 18px; margin-bottom: 2px; }
    .nav-item.active { color: #0d47a1; }
</style>
"""

SIDE_MENU_HTML = """
<div class="menu-overlay" id="menuOverlay" onclick="toggleMenu()"></div>
<div class="side-menu" id="sideMenu">
    <div class="menu-header">
        <i class="fas fa-user-circle"></i>
        <div>
            <div style="font-weight: bold; font-size: 15px;">Login or Register</div>
            <div style="font-size: 11px; opacity: 0.8;">Sync your preferences</div>
        </div>
    </div>
    <a href="/standings" class="menu-item"><i class="fas fa-trophy"></i> Competitions</a>
    <a href="/favourites" class="menu-item"><i class="fas fa-shield-alt"></i> Teams</a>
    <a href="/topscorers" class="menu-item"><i class="fas fa-running"></i> Players</a>
    <a href="/transfers" class="menu-item"><i class="fas fa-exchange-alt"></i> Transfers</a>
    <a href="/" class="menu-item"><i class="fas fa-search"></i> Find Match</a>
    
    <div class="menu-divider">More Options</div>
    <a href="#" class="menu-item"><i class="fas fa-ad"></i> Remove Ads</a>
    <a href="#" class="menu-item"><i class="fas fa-cog"></i> Settings</a>
    <a href="/privacy-policy" class="menu-item"><i class="fas fa-info-circle"></i> About Us</a>
    <a href="#" class="menu-item"><i class="fas fa-bug"></i> Report Incidence</a>
</div>
"""

BOTTOM_NAV_HTML = """
<div class="bottom-nav">
    <a href="/" class="nav-item {% if active_tab == 'matches' %}active{% endif %}">
        <i class="fas fa-futbol"></i> Matches
    </a>
    <a href="/favourites" class="nav-item {% if active_tab == 'favourites' %}active{% endif %}">
        <i class="fas fa-star"></i> Favourites
    </a>
    <a href="/explore" class="nav-item {% if active_tab == 'explore' %}active{% endif %}">
        <i class="fas fa-compass"></i> Explore
    </a>
    <a href="/transfers" class="nav-item {% if active_tab == 'transfers' %}active{% endif %}">
        <i class="fas fa-exchange-alt"></i> Transfers
    </a>
    <a href="/news" class="nav-item {% if active_tab == 'news' %}active{% endif %}">
        <i class="fas fa-newspaper"></i> News
    </a>
</div>
"""

@app.route('/privacy-policy')
def privacy_policy():
    return "<h2>Privacy Policy</h2><p>Koki Score provides live sports updates. We do not collect or share personal information.</p>"

# 1. MATCHES (HOME)
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
                comps = event.get('competitions', [{}])
                if not comps: continue
                comp = comps[0]
                competitors = comp.get('competitors', [{}, {}])
                if len(competitors) < 2: continue

                home_team = competitors[0]
                away_team = competitors[1]
                
                status_state = event.get('status', {}).get('type', {}).get('state', '')
                detail = event.get('status', {}).get('type', {}).get('shortDetail', '')
                event_date = event.get('date', '')
                start_time = format_kickoff_time(event_date)

                if status_state == 'in':
                    status = "LIVE"
                elif status_state == 'post':
                    status = "FINISHED"
                else:
                    status = "UPCOMING"
                    if start_time:
                        detail = f"⏰ {start_time}"

                league_name = extract_league_name(event)

                matches.append({
                    "id": event.get('id'),
                    "league": league_name,
                    "home": home_team.get('team', {}).get('displayName', 'Home'),
                    "home_logo": home_team.get('team', {}).get('logo', ''),
                    "home_score": home_team.get('score', '0'),
                    "away": away_team.get('team', {}).get('displayName', 'Away'),
                    "away_logo": away_team.get('team', {}).get('logo', ''),
                    "away_score": away_team.get('score', '0'),
                    "status": status,
                    "detail": detail,
                    "start_time": start_time
                })
    except Exception as e:
        print("Error fetching matches:", e)

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Koki Score - Matches</title>
        """ + PWA_HEADER + COMMON_STYLE + SOCIAL_BAR_CODE + INTERSTITIAL_AD_CODE + """
        <style>
            .date-picker { background: white; padding: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
            .date-picker input { padding: 8px 14px; border: 1px solid #ccc; border-radius: 6px; font-size: 14px; outline: none; font-weight: bold; color: #0d47a1; }
            .match-card { background: white; border-radius: 10px; padding: 12px; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); display: block; text-decoration: none; color: inherit; }
            .league-title { font-size: 11px; font-weight: bold; color: #0d47a1; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f0f0f0; padding-bottom: 4px; }
            .match-header { font-size: 11px; color: #666; text-transform: uppercase; margin-bottom: 8px; font-weight: bold; display: flex; align-items: center; justify-content: space-between; }
            .teams { display: flex; justify-content: space-between; align-items: center; }
            .team { display: flex; align-items: center; width: 40%; font-size: 13px; font-weight: 500; }
            .team.away { justify-content: flex-end; }
            .logo { width: 24px; height: 24px; margin: 0 6px; object-fit: contain; }
            .score { font-size: 18px; font-weight: bold; background: #0d47a1; color: white; padding: 4px 10px; border-radius: 6px; }
            .badge { font-size: 10px; padding: 3px 6px; border-radius: 4px; font-weight: bold; display: inline-block; }
            .LIVE { background: #ffebee; color: #c62828; }
            .FINISHED { background: #e8f5e9; color: #2e7d32; }
            .UPCOMING { background: #e3f2fd; color: #1565c0; }
            .time-text { font-size: 11px; font-weight: bold; color: #2e7d32; background: #e8f5e9; padding: 2px 6px; border-radius: 4px; }
        </style>
    </head>
    <body>
        """ + SIDE_MENU_HTML + """
        <div class="top-bar">
            <button class="icon-btn" onclick="toggleMenu()"><i class="fas fa-bars"></i></button>
            <span>⚽ Koki Score</span>
            <i class="fas fa-search icon-btn"></i>
        </div>
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
                    {% if m.start_time %}
                        <span class="time-text">🕒 {{ m.start_time }}</span>
                    {% endif %}
                </div>
                <div class="teams">
                    <div class="team">
                        <img class="logo" src="{{ m.home_logo }}" onerror="this.src='https://cdn-icons-png.flaticon.com/512/5328/5328320.png'">
                        <span>{{ m.home }}</span>
                    </div>
                    <div class="score">{{ m.home_score }} - {{ m.away_score }}</div>
                    <div class="team away">
                        <span>{{ m.away }}</span>
                        <img class="logo" src="{{ m.away_logo }}" onerror="this.src='https://cdn-icons-png.flaticon.com/512/5328/5328320.png'">
                    </div>
                </div>
            </a>
            {% else %}
            <p style="text-align:center; color: #777; padding: 20px;">No matches found for the selected date.</p>
            {% endfor %}
            """ + BANNER_AD_CODE + """
        </div>
        """ + BOTTOM_NAV_HTML + PWA_SCRIPT + """
    </body>
    </html>
    """, matches=matches, selected_date=selected_date, active_tab='matches')

# 2. FAVOURITES TAB
@app.route('/favourites')
def favourites():
    popular_teams = [
        {"name": "Arsenal", "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/359.png"},
        {"name": "Manchester United", "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/360.png"},
        {"name": "Manchester City", "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/382.png"},
        {"name": "Liverpool", "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/364.png"},
        {"name": "Chelsea", "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/363.png"},
        {"name": "Real Madrid", "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/86.png"},
        {"name": "FC Barcelona", "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/83.png"},
        {"name": "Bayern München", "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/132.png"},
        {"name": "PSG", "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/160.png"}
    ]
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Favourites - Koki Score</title>
        """ + PWA_HEADER + COMMON_STYLE + SOCIAL_BAR_CODE + """
        <style>
            .grid-teams { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 15px; }
            .team-card { background: white; border-radius: 10px; padding: 15px 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.03); position: relative; }
            .team-card img { width: 45px; height: 45px; object-fit: contain; margin-bottom: 8px; }
            .team-card div { font-size: 12px; font-weight: bold; color: #333; }
            .fav-star { position: absolute; top: 6px; right: 8px; color: #ccc; font-size: 14px; cursor: pointer; }
        </style>
    </head>
    <body>
        """ + SIDE_MENU_HTML + """
        <div class="top-bar">
            <button class="icon-btn" onclick="toggleMenu()"><i class="fas fa-bars"></i></button>
            <span>⭐ Favourites</span>
            <i class="fas fa-cog icon-btn"></i>
        </div>
        <div class="container">
            <div style="font-size: 12px; font-weight: bold; color: #666; margin: 10px 0 5px 0; text-transform: uppercase;">Most Wanted Teams</div>
            <div class="grid-teams">
                {% for team in teams %}
                <div class="team-card">
                    <i class="far fa-star fav-star"></i>
                    <img src="{{ team.logo }}" onerror="this.src='https://cdn-icons-png.flaticon.com/512/5328/5328320.png'">
                    <div>{{ team.name }}</div>
                </div>
                {% endfor %}
            </div>
            """ + BANNER_AD_CODE + """
        </div>
        """ + BOTTOM_NAV_HTML + PWA_SCRIPT + """
    </body>
    </html>
    """, teams=popular_teams, active_tab='favourites')

# 3. EXPLORE TAB
@app.route('/explore')
def explore():
    countries = [
        {"name": "Ethiopia", "flag": "🇪🇹", "comps": "3 Competitions"},
        {"name": "Spain", "flag": "🇪🇸", "comps": "986 Competitions"},
        {"name": "England", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "comps": "39 Competitions"},
        {"name": "Italy", "flag": "🇮🇹", "comps": "41 Competitions"},
        {"name": "Germany", "flag": "🇩🇪", "comps": "28 Competitions"},
        {"name": "Argentina", "flag": "🇦🇷", "comps": "15 Competitions"},
        {"name": "Brazil", "flag": "🇧🇷", "comps": "22 Competitions"}
    ]
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Explore - Koki Score</title>
        """ + PWA_HEADER + COMMON_STYLE + SOCIAL_BAR_CODE + """
        <style>
            .search-box { background: white; padding: 10px 15px; border-radius: 8px; display: flex; align-items: center; gap: 10px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.03); }
            .search-box input { border: none; outline: none; width: 100%; font-size: 14px; }
            .country-item { background: white; padding: 12px 15px; border-radius: 8px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
            .c-flag { font-size: 20px; margin-right: 12px; }
            .c-name { font-size: 14px; font-weight: bold; color: #222; }
            .c-sub { font-size: 11px; color: #777; }
        </style>
    </head>
    <body>
        """ + SIDE_MENU_HTML + """
        <div class="top-bar">
            <button class="icon-btn" onclick="toggleMenu()"><i class="fas fa-bars"></i></button>
            <span>🔍 Explore</span>
            <i class="fas fa-search icon-btn"></i>
        </div>
        <div class="container">
            <div class="search-box">
                <i class="fas fa-search" style="color: #888;"></i>
                <input type="text" placeholder="Search countries or leagues...">
            </div>
            <div style="font-size: 12px; font-weight: bold; color: #666; margin-bottom: 10px;">FEATURED COUNTRIES</div>
            {% for c in countries %}
            <div class="country-item">
                <div style="display: flex; align-items: center;">
                    <span class="c-flag">{{ c.flag }}</span>
                    <div>
                        <div class="c-name">{{ c.name }}</div>
                        <div class="c-sub">{{ c.comps }}</div>
                    </div>
                </div>
                <i class="fas fa-shield-alt" style="color: #ccc;"></i>
            </div>
            {% endfor %}
            """ + BANNER_AD_CODE + """
        </div>
        """ + BOTTOM_NAV_HTML + PWA_SCRIPT + """
    </body>
    </html>
    """, countries=countries, active_tab='explore')

# 4. TRANSFERS TAB
@app.route('/transfers')
def transfers():
    transfers_data = [
        {"player": "J. Correa", "pos": "MD", "text": "Estudiantes La Plata sign J. Correa from Botafogo on a free transfer", "type": "OFFICIAL"},
        {"player": "M. Kumbulla", "pos": "DF", "text": "Roma have loaned M. Kumbulla to Rayo Vallecano", "type": "OFFICIAL"},
        {"player": "O. Mangala", "pos": "MD", "text": "Olympique Lyonnais have loaned O. Mangala to Getafe", "type": "OFFICIAL"},
        {"player": "T. Tomiyasu", "pos": "DF", "text": "Crystal Palace sign T. Tomiyasu from Ajax on a free transfer", "type": "OFFICIAL"}
    ]
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Transfers - Koki Score</title>
        """ + PWA_HEADER + COMMON_STYLE + SOCIAL_BAR_CODE + """
        <style>
            .transfer-card { background: white; padding: 12px; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
            .t-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
            .t-pos { background: #4caf50; color: white; font-size: 10px; padding: 2px 5px; border-radius: 3px; font-weight: bold; }
            .t-name { font-weight: bold; font-size: 13px; color: #111; }
            .t-text { font-size: 12px; color: #555; line-height: 1.4; }
        </style>
    </head>
    <body>
        """ + SIDE_MENU_HTML + """
        <div class="top-bar">
            <button class="icon-btn" onclick="toggleMenu()"><i class="fas fa-bars"></i></button>
            <span>🔄 Transfers</span>
            <i class="fas fa-filter icon-btn"></i>
        </div>
        <div class="container">
            <div style="font-size: 11px; font-weight: bold; color: #888; margin-bottom: 8px;">LATEST TRANSFERS</div>
            {% for t in transfers %}
            <div class="transfer-card">
                <div class="t-header">
                    <span class="t-pos">{{ t.pos }}</span>
                    <span class="t-name">{{ t.player }}</span>
                </div>
                <div class="t-text">{{ t.text }}</div>
            </div>
            {% endfor %}
            """ + BANNER_AD_CODE + """
        </div>
        """ + BOTTOM_NAV_HTML + PWA_SCRIPT + """
    </body>
    </html>
    """, transfers=transfers_data, active_tab='transfers')

# 5. NEWS TAB
@app.route('/news')
def news():
    news_items = [
        {
            "title": "Diomande completes medical but Real Madrid debut delayed",
            "desc": "Ivorian winger Yan Diomande was pictured ahead of his medical on Friday, but administrative details...",
            "time": "3 hours ago",
            "img": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=500&auto=format&fit=crop&q=60"
        },
        {
            "title": "Pre-season highlights: Top tactical shifts ahead of the new season",
            "desc": "European giants wrap up tour friendlies with surprising lineup experiments...",
            "time": "5 hours ago",
            "img": "https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=500&auto=format&fit=crop&q=60"
        }
    ]
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>News - Koki Score</title>
        """ + PWA_HEADER + COMMON_STYLE + SOCIAL_BAR_CODE + """
        <style>
            .news-card { background: white; border-radius: 10px; overflow: hidden; margin-bottom: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); }
            .news-img { width: 100%; height: 160px; object-fit: cover; }
            .news-body { padding: 12px; }
            .news-title { font-size: 14px; font-weight: bold; color: #111; margin-bottom: 6px; }
            .news-desc { font-size: 12px; color: #666; margin-bottom: 8px; line-height: 1.4; }
            .news-time { font-size: 10px; color: #999; }
        </style>
    </head>
    <body>
        """ + SIDE_MENU_HTML + """
        <div class="top-bar">
            <button class="icon-btn" onclick="toggleMenu()"><i class="fas fa-bars"></i></button>
            <span>📰 Football News</span>
            <i class="fas fa-search icon-btn"></i>
        </div>
        <div class="container">
            {% for item in news_items %}
            <div class="news-card">
                <img src="{{ item.img }}" class="news-img" onerror="this.src='https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=500'">
                <div class="news-body">
                    <div class="news-title">{{ item.title }}</div>
                    <div class="news-desc">{{ item.desc }}</div>
                    <div class="news-time">🕒 {{ item.time }}</div>
                </div>
            </div>
            {% endfor %}
            """ + BANNER_AD_CODE + """
        </div>
        """ + BOTTOM_NAV_HTML + PWA_SCRIPT + """
    </body>
    </html>
    """, news_items=news_items, active_tab='news')

# 6. MATCH DETAILS
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
            competitors = header.get('competitors', [{}, {}])
            home_team = competitors[0] if len(competitors) > 0 else {}
            away_team = competitors[1] if len(competitors) > 1 else {}
            
            league_name = data.get('header', {}).get('league', {}).get('displayName') or data.get('header', {}).get('league', {}).get('name', 'Football Match')

            match_data = {
                "league": league_name,
                "home": home_team.get('team', {}).get('displayName', 'Home'),
                "home_score": home_team.get('score', '0'),
                "away": away_team.get('team', {}).get('displayName', 'Away'),
                "away_score": away_team.get('score', '0'),
                "status": header.get('status', {}).get('type', {}).get('shortDetail', 'FT')
            }
            
            key_events = data.get('keyEvents', [])
            for k in key_events:
                events.append({
                    "time": k.get('clock', {}).get('displayValue', ''),
                    "text": k.get('text', ''),
                    "type": k.get('type', {}).get('text', '')
                })

            boxscore = data.get('boxscore', {}).get('teams', [])
            if len(boxscore) == 2:
                home_stats = {s['name']: s['displayValue'] for s in boxscore[0].get('statistics', []) if 'name' in s}
                away_stats = {s['name']: s['displayValue'] for s in boxscore[1].get('statistics', []) if 'name' in s}
                
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
        """ + PWA_HEADER + COMMON_STYLE + SOCIAL_BAR_CODE + INTERSTITIAL_AD_CODE + """
        <style>
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
        """ + SIDE_MENU_HTML + """
        <div class="top-bar">
            <button class="icon-btn" onclick="toggleMenu()"><i class="fas fa-bars"></i></button>
            <span>⚽ Match Details</span>
            <a href="/" class="icon-btn" style="font-size: 14px;">Home</a>
        </div>
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

            """ + BANNER_AD_CODE + """

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
        """ + BOTTOM_NAV_HTML + PWA_SCRIPT + """
    </body>
    </html>
    """, match=match_data, events=events, stats=stats, active_tab='matches')

# 7. STANDINGS
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
                
                rank_val = stats.get('rank', idx) or idx

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
        <title>Standings - Koki Score</title>
        """ + PWA_HEADER + COMMON_STYLE + SOCIAL_BAR_CODE + """
        <style>
            .league-selector { display: flex; overflow-x: auto; background: #1565c0; padding: 8px; scrollbar-width: none; }
            .league-btn { color: #bbdefb; text-decoration: none; padding: 6px 12px; font-size: 12px; font-weight: bold; border-radius: 15px; white-space: nowrap; margin-right: 5px; }
            .league-btn.active { background: #ffeb3b; color: #0d47a1; }
            table { width: 100%; background: white; border-collapse: collapse; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.03); font-size: 12px; }
            th { background: #f0f4f8; color: #333; padding: 8px 4px; text-align: center; font-weight: bold; }
            td { padding: 8px 4px; text-align: center; border-bottom: 1px solid #eee; }
            .team-cell { display: flex; align-items: center; text-align: left; font-weight: bold; color: #111; }
            .team-logo { width: 18px; height: 18px; margin-right: 6px; object-fit: contain; }
            .pts-col { background: #e3f2fd; font-weight: bold; color: #0d47a1; }
        </style>
    </head>
    <body>
        """ + SIDE_MENU_HTML + """
        <div class="top-bar">
            <button class="icon-btn" onclick="toggleMenu()"><i class="fas fa-bars"></i></button>
            <span>📊 Standings</span>
            <i class="fas fa-search icon-btn"></i>
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
                        <th>PTS</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in standings %}
                    <tr>
                        <td style="color:#0d47a1; font-weight:bold;">{{ row.rank }}</td>
                        <td class="team-cell">
                            {% if row.logo %}<img src="{{ row.logo }}" class="team-logo" onerror="this.style.display='none'">{% endif %}
                            <span>{{ row.team }}</span>
                        </td>
                        <td>{{ row.played }}</td>
                        <td>{{ row.wins }}</td>
                        <td>{{ row.draws }}</td>
                        <td>{{ row.losses }}</td>
                        <td class="pts-col">{{ row.pts }}</td>
                    </tr>
                    {% else %}
                    <tr><td colspan="7">No standings data available.</td></tr>
                    {% endfor %}
                </tbody>
            </table>
            """ + BANNER_AD_CODE + """
        </div>
        """ + BOTTOM_NAV_HTML + PWA_SCRIPT + """
    </body>
    </html>
    """, standings=standings_data, leagues=LEAGUES_MAP, selected_league=league_code, active_tab='matches')

# 8. TOP SCORERS
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
        """ + PWA_HEADER + COMMON_STYLE + SOCIAL_BAR_CODE + """
        <style>
            .league-selector { display: flex; overflow-x: auto; background: #1565c0; padding: 8px; scrollbar-width: none; }
            .league-btn { color: #bbdefb; text-decoration: none; padding: 6px 12px; font-size: 12px; font-weight: bold; border-radius: 15px; white-space: nowrap; margin-right: 5px; }
            .league-btn.active { background: #ffeb3b; color: #0d47a1; }
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
        """ + SIDE_MENU_HTML + """
        <div class="top-bar">
            <button class="icon-btn" onclick="toggleMenu()"><i class="fas fa-bars"></i></button>
            <span>⚽ Top Scorers</span>
            <i class="fas fa-search icon-btn"></i>
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
                            <img src="{{ player.headshot }}" class="player-img" onerror="this.style.display='none'">
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
            """ + BANNER_AD_CODE + """
        </div>
        """ + BOTTOM_NAV_HTML + PWA_SCRIPT + """
    </body>
    </html>
    """, scorers=scorers_data, leagues=LEAGUES_MAP, selected_league=league_code, active_tab='matches')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
