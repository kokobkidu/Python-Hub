from flask import Flask, render_template_string, jsonify, request
import requests

app = Flask(__name__)

# Free Sports API Endpoints
SPORTS_API_BASE = "https://www.thesportsdb.com/api/v1/json/3"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Koki Score - Live Football Updates</title>
    <link rel="manifest" href="/static/manifest.json">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary-color: #0d47a1; /* Koki Score Original Blue */
            --primary-dark: #002171;
            --secondary-color: #1565c0;
            --bg-color: #f4f6f9;
            --card-bg: #ffffff;
            --text-color: #212121;
            --light-text: #666666;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            padding-bottom: 70px;
            padding-top: 60px;
        }

        /* Top Header */
        header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 56px;
            background-color: var(--primary-color);
            color: white;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 16px;
            z-index: 1000;
            box-shadow: 0 2px 6px rgba(0,0,0,0.25);
        }

        header .logo-area {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 1.2rem;
            font-weight: bold;
        }

        header .header-icons {
            display: flex;
            gap: 18px;
            font-size: 1.1rem;
        }

        header i {
            cursor: pointer;
        }

        /* Side Navigation Drawer */
        .side-drawer {
            position: fixed;
            top: 0;
            left: -290px;
            width: 280px;
            height: 100%;
            background: white;
            z-index: 2000;
            transition: all 0.3s ease;
            box-shadow: 3px 0 12px rgba(0,0,0,0.3);
            overflow-y: auto;
        }

        .side-drawer.active {
            left: 0;
        }

        .drawer-overlay {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.5);
            display: none;
            z-index: 1500;
        }

        .drawer-overlay.active {
            display: block;
        }

        .drawer-header {
            padding: 24px 20px;
            background: var(--primary-color);
            color: white;
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .drawer-menu {
            list-style: none;
            padding: 10px 0;
        }

        .drawer-menu li a {
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 13px 20px;
            color: var(--text-color);
            text-decoration: none;
            font-size: 0.95rem;
            font-weight: 500;
        }

        .drawer-menu li a:hover {
            background: #e3f2fd;
            color: var(--primary-color);
        }

        .drawer-divider {
            height: 1px;
            background: #e0e0e0;
            margin: 8px 0;
        }

        /* Date Sub-Bar for Matches */
        .date-bar {
            display: flex;
            justify-content: space-around;
            background: var(--primary-dark);
            color: white;
            padding: 10px 5px;
            font-size: 0.8rem;
            margin: -10px -10px 12px -10px;
            font-weight: 600;
        }

        .date-item {
            padding: 4px 10px;
            border-radius: 12px;
            cursor: pointer;
            opacity: 0.8;
        }

        .date-item.active {
            background: #ffffff;
            color: var(--primary-dark);
            opacity: 1;
        }

        /* Bottom Navigation Bar */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 60px;
            background-color: #ffffff;
            display: flex;
            justify-content: space-around;
            align-items: center;
            border-top: 1px solid #e0e0e0;
            z-index: 1000;
            box-shadow: 0 -1px 4px rgba(0,0,0,0.08);
        }

        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            color: #757575;
            text-decoration: none;
            font-size: 0.72rem;
            cursor: pointer;
            width: 20%;
        }

        .nav-item i {
            font-size: 1.25rem;
            margin-bottom: 3px;
        }

        .nav-item.active {
            color: var(--primary-color);
            font-weight: bold;
        }

        /* Container Tab Views */
        .tab-content {
            display: none;
            padding: 10px;
        }

        .tab-content.active {
            display: block;
        }

        /* Matches Card UI */
        .league-card {
            background: white;
            border-radius: 8px;
            margin-bottom: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .league-header {
            background: #e3f2fd;
            padding: 8px 12px;
            font-size: 0.85rem;
            font-weight: bold;
            color: var(--primary-dark);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .match-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 12px;
            border-bottom: 1px solid #f0f0f0;
        }

        .match-row:last-child {
            border-bottom: none;
        }

        .team-info {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.9rem;
            font-weight: 500;
            width: 40%;
        }

        .team-info.away {
            justify-content: flex-end;
            text-align: right;
        }

        .team-badge {
            width: 24px;
            height: 24px;
            object-fit: contain;
        }

        .match-score {
            font-weight: bold;
            font-size: 0.95rem;
            background: #f0f0f0;
            padding: 4px 10px;
            border-radius: 4px;
            color: var(--primary-dark);
        }

        /* Favourites Grid */
        .fav-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            padding: 5px 0;
        }

        .fav-card {
            background: white;
            padding: 12px 8px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            font-size: 0.82rem;
            font-weight: bold;
        }

        .fav-card img {
            width: 42px;
            height: 42px;
            object-fit: contain;
            margin-bottom: 6px;
        }

        /* Search Input for Explore */
        .search-box {
            width: 100%;
            padding: 10px 16px;
            border: 1px solid #ccc;
            border-radius: 20px;
            margin-bottom: 14px;
            outline: none;
            font-size: 0.9rem;
        }

        /* News & Transfer Style */
        .news-card {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .news-card img {
            width: 100%;
            height: 170px;
            object-fit: cover;
        }

        .news-body {
            padding: 12px;
        }

        .news-title {
            font-weight: bold;
            font-size: 0.95rem;
            margin-bottom: 6px;
            color: var(--primary-dark);
        }

        .news-desc {
            font-size: 0.83rem;
            color: var(--light-text);
            line-height: 1.3;
        }
    </style>
</head>
<body>

    <!-- Header -->
    <header>
        <div class="logo-area">
            <i class="fas fa-bars" onclick="toggleDrawer()"></i>
            <span>Koki Score</span>
        </div>
        <div class="header-icons">
            <i class="fas fa-calendar-day" onclick="switchTab('matches', document.querySelectorAll('.nav-item')[0])"></i>
            <i class="fas fa-search" onclick="switchTab('explore', document.querySelectorAll('.nav-item')[2])"></i>
        </div>
    </header>

    <!-- Side Navigation Drawer -->
    <div class="drawer-overlay" id="overlay" onclick="toggleDrawer()"></div>
    <div class="side-drawer" id="drawer">
        <div class="drawer-header">
            <i class="fas fa-user-circle fa-2x"></i>
            <div>
                <div style="font-weight:bold;">Welcome to Koki Score</div>
                <div style="font-size:0.78rem; opacity:0.8;">Login or Register</div>
            </div>
        </div>
        <ul class="drawer-menu">
            <li><a href="#" onclick="toggleDrawer(); switchTab('matches', document.querySelectorAll('.nav-item')[0]);"><i class="fas fa-futbol"></i> Matches</a></li>
            <li><a href="#" onclick="toggleDrawer(); switchTab('favourites', document.querySelectorAll('.nav-item')[1]);"><i class="fas fa-star"></i> Favourites</a></li>
            <li><a href="#" onclick="toggleDrawer(); switchTab('explore', document.querySelectorAll('.nav-item')[2]);"><i class="fas fa-trophy"></i> Competitions</a></li>
            <li><a href="#" onclick="toggleDrawer(); switchTab('transfers', document.querySelectorAll('.nav-item')[3]);"><i class="fas fa-exchange-alt"></i> Transfers</a></li>
            <li><a href="#" onclick="toggleDrawer(); switchTab('news', document.querySelectorAll('.nav-item')[4]);"><i class="fas fa-newspaper"></i> News</a></li>
            <div class="drawer-divider"></div>
            <li><a href="#"><i class="fas fa-cog"></i> Settings</a></li>
            <li><a href="#"><i class="fas fa-info-circle"></i> About Koki Score</a></li>
        </ul>
    </div>

    <!-- TAB 1: MATCHES -->
    <div id="tab-matches" class="tab-content active">
        <div class="date-bar">
            <span class="date-item" onclick="filterDate('yesterday', this)">YESTERDAY</span>
            <span class="date-item active" onclick="filterDate('today', this)">TODAY</span>
            <span class="date-item" onclick="filterDate('live', this)">LIVE</span>
            <span class="date-item" onclick="filterDate('tomorrow', this)">TOMORROW</span>
        </div>
        <div id="matches-container">
            <!-- Matches Dynamically Loaded -->
            <div class="league-card">
                <div class="league-header"><i class="fas fa-globe"></i> INTERNATIONAL FRIENDLIES</div>
                <div class="match-row">
                    <div class="team-info">
                        <img src="https://www.thesportsdb.com/images/media/team/badge/small/v935391583002237.png" class="team-badge" onerror="this.src='https://cdn-icons-png.flaticon.com/512/53/53283.png'">
                        <span>Bayern München</span>
                    </div>
                    <span class="match-score">2 - 1</span>
                    <div class="team-info away">
                        <span>Aston Villa</span>
                        <img src="https://www.thesportsdb.com/images/media/team/badge/small/3283281583002237.png" class="team-badge" onerror="this.src='https://cdn-icons-png.flaticon.com/512/53/53283.png'">
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- TAB 2: FAVOURITES -->
    <div id="tab-favourites" class="tab-content">
        <h3 style="margin-bottom:12px; color:var(--primary-dark);">Most Wanted Teams</h3>
        <div class="fav-grid">
            <div class="fav-card">
                <img src="https://www.thesportsdb.com/images/media/team/badge/small/uvxuqq1448813372.png">
                <div>Arsenal</div>
            </div>
            <div class="fav-card">
                <img src="https://www.thesportsdb.com/images/media/team/badge/small/tyytxu1448813373.png">
                <div>Man United</div>
            </div>
            <div class="fav-card">
                <img src="https://www.thesportsdb.com/images/media/team/badge/small/txtrur1448813373.png">
                <div>Man City</div>
            </div>
            <div class="fav-card">
                <img src="https://www.thesportsdb.com/images/media/team/badge/small/0002151522071853.png">
                <div>Real Madrid</div>
            </div>
            <div class="fav-card">
                <img src="https://www.thesportsdb.com/images/media/team/badge/small/1831121522071853.png">
                <div>Barcelona</div>
            </div>
            <div class="fav-card">
                <img src="https://www.thesportsdb.com/images/media/team/badge/small/1739121522071853.png">
                <div>Liverpool</div>
            </div>
        </div>
    </div>

    <!-- TAB 3: EXPLORE -->
    <div id="tab-explore" class="tab-content">
        <input type="text" class="search-box" placeholder="Search countries, leagues, or teams...">
        <h4 style="margin-bottom:10px; color:var(--primary-dark);">Featured Countries</h4>
        <ul style="list-style:none;">
            <li style="padding:12px; background:white; margin-bottom:6px; border-radius:6px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 1px 2px rgba(0,0,0,0.05);">
                <span>🇪🇹 Ethiopia (Premier League)</span>
                <span style="color:#888; font-size:0.85rem;">3 Comps</span>
            </li>
            <li style="padding:12px; background:white; margin-bottom:6px; border-radius:6px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 1px 2px rgba(0,0,0,0.05);">
                <span>🏴󠁧󠁢󠁥󠁮󠁧󠁿 England (Premier League)</span>
                <span style="color:#888; font-size:0.85rem;">39 Comps</span>
            </li>
            <li style="padding:12px; background:white; margin-bottom:6px; border-radius:6px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 1px 2px rgba(0,0,0,0.05);">
                <span>🇪🇸 Spain (La Liga)</span>
                <span style="color:#888; font-size:0.85rem;">98 Comps</span>
            </li>
        </ul>
    </div>

    <!-- TAB 4: TRANSFERS -->
    <div id="tab-transfers" class="tab-content">
        <h3 style="margin-bottom:12px; color:var(--primary-dark);">Latest Transfers</h3>
        <div class="news-card">
            <div class="news-body">
                <div class="news-title">J. Correa ➡️ Botafogo to Estudiantes</div>
                <p class="news-desc">Official: Loan deal completed on free transfer terms.</p>
            </div>
        </div>
        <div class="news-card">
            <div class="news-body">
                <div class="news-title">M. Kumbulla ➡️ Roma to Rayo Vallecano</div>
                <p class="news-desc">Official: Loan agreement signed for the upcoming season.</p>
            </div>
        </div>
    </div>

    <!-- TAB 5: NEWS -->
    <div id="tab-news" class="tab-content">
        <h3 style="margin-bottom:12px; color:var(--primary-dark);">Football News</h3>
        <div class="news-card">
            <img src="https://www.thesportsdb.com/images/media/player/thumb/p138371583002237.jpg" alt="News Image">
            <div class="news-body">
                <div class="news-title">Diomande completes medical ahead of transfer</div>
                <p class="news-desc">Ivorian winger Yan Diomande was pictured ahead of his medical checks today...</p>
            </div>
        </div>
    </div>

    <!-- Bottom Navigation Bar -->
    <nav class="bottom-nav">
        <div class="nav-item active" onclick="switchTab('matches', this)">
            <i class="fas fa-futbol"></i>
            <span>Matches</span>
        </div>
        <div class="nav-item" onclick="switchTab('favourites', this)">
            <i class="far fa-star"></i>
            <span>Favourites</span>
        </div>
        <div class="nav-item" onclick="switchTab('explore', this)">
            <i class="fas fa-compass"></i>
            <span>Explore</span>
        </div>
        <div class="nav-item" onclick="switchTab('transfers', this)">
            <i class="fas fa-exchange-alt"></i>
            <span>Transfers</span>
        </div>
        <div class="nav-item" onclick="switchTab('news', this)">
            <i class="far fa-newspaper"></i>
            <span>News</span>
        </div>
    </nav>

    <script>
        function toggleDrawer() {
            document.getElementById('drawer').classList.toggle('active');
            document.getElementById('overlay').classList.toggle('active');
        }

        function switchTab(tabId, element) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));

            document.getElementById('tab-' + tabId).classList.add('active');
            if(element) element.classList.add('active');
        }

        function filterDate(type, element) {
            document.querySelectorAll('.date-item').forEach(item => item.classList.remove('active'));
            element.classList.add('active');
            // Fetch filtered matches using existing Flask logic
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True)
