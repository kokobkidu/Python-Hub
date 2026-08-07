from flask import Flask, render_template_string, jsonify, request
import requests

app = Flask(__name__)

# Free Football API Endpoint
API_URL = "https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d=2024-05-19&s=Soccer"

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
            --primary-color: #003399; /* Koki Score Original Blue */
            --primary-dark: #002266;
            --bg-color: #f4f5f7;
            --card-bg: #ffffff;
            --text-color: #333333;
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
            padding-top: 55px;
        }

        /* Top Header */
        header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 55px;
            background-color: var(--primary-color);
            color: white;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 15px;
            z-index: 1000;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }

        header .logo {
            font-size: 1.2rem;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        header .header-icons {
            display: flex;
            gap: 18px;
            font-size: 1.2rem;
        }

        /* Side Navigation Drawer */
        .side-drawer {
            position: fixed;
            top: 0;
            left: -280px;
            width: 270px;
            height: 100%;
            background: white;
            z-index: 2000;
            transition: 0.3s;
            box-shadow: 2px 0 10px rgba(0,0,0,0.3);
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
            padding: 20px;
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
            gap: 15px;
            padding: 12px 20px;
            color: #333;
            text-decoration: none;
            font-size: 0.95rem;
        }

        .drawer-menu li a:hover {
            background: #e6ecf8;
            color: var(--primary-color);
        }

        .drawer-divider {
            height: 1px;
            background: #eee;
            margin: 10px 0;
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
        }

        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            color: #757575;
            text-decoration: none;
            font-size: 0.75rem;
            cursor: pointer;
            width: 20%;
        }

        .nav-item i {
            font-size: 1.2rem;
            margin-bottom: 3px;
        }

        .nav-item.active {
            color: var(--primary-color);
            font-weight: bold;
        }

        /* Views Layout */
        .tab-content {
            display: none;
            padding: 10px;
        }

        .tab-content.active {
            display: block;
        }

        /* Sub Date Header for Matches */
        .date-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--primary-dark);
            color: white;
            padding: 8px 15px;
            font-size: 0.8rem;
            font-weight: bold;
            margin: -10px -10px 12px -10px;
        }

        .date-btn {
            padding: 4px 10px;
            border-radius: 15px;
            cursor: pointer;
            opacity: 0.8;
        }

        .date-btn.active {
            background: white;
            color: var(--primary-dark);
            opacity: 1;
        }

        /* Match Card UI - Screenshot Match */
        .match-card {
            background: white;
            border-radius: 8px;
            margin-bottom: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            overflow: hidden;
        }

        .league-title {
            background: #e8f0fe;
            font-size: 0.8rem;
            font-weight: bold;
            color: var(--primary-color);
            padding: 8px 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .match-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
        }

        .team-side {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
            font-size: 0.9rem;
            flex: 1;
        }

        .team-side.away {
            justify-content: flex-end;
        }

        .team-logo {
            width: 24px;
            height: 24px;
            object-fit: contain;
        }

        .score-box {
            font-weight: bold;
            font-size: 0.9rem;
            background: #f0f4f9;
            color: var(--primary-dark);
            padding: 3px 10px;
            border-radius: 4px;
            margin: 0 8px;
        }

        /* Favourites Grid */
        .fav-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            text-align: center;
            padding: 10px 0;
        }

        .fav-item {
            background: white;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            font-size: 0.8rem;
        }

        .fav-item img {
            width: 40px;
            height: 40px;
            margin-bottom: 5px;
        }

        /* Explore Search */
        .search-box {
            width: 100%;
            padding: 10px 14px;
            border: 1px solid #ccc;
            border-radius: 20px;
            margin-bottom: 15px;
            outline: none;
        }

        /* News & Transfer Card */
        .news-card {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .news-card img {
            width: 100%;
            height: 180px;
            object-fit: cover;
        }

        .news-content {
            padding: 12px;
        }

        .news-title {
            font-weight: bold;
            font-size: 0.95rem;
            margin-bottom: 5px;
            color: var(--primary-dark);
        }

        .news-desc {
            font-size: 0.85rem;
            color: #666;
        }
    </style>
</head>
<body>

    <!-- Header -->
    <header>
        <div class="logo">
            <i class="fas fa-bars" onclick="toggleDrawer()"></i>
            <span>Koki Score</span>
        </div>
        <div class="header-icons">
            <i class="fas fa-calendar-alt"></i>
            <i class="fas fa-search"></i>
        </div>
    </header>

    <!-- Side Drawer -->
    <div class="drawer-overlay" id="overlay" onclick="toggleDrawer()"></div>
    <div class="side-drawer" id="drawer">
        <div class="drawer-header">
            <i class="fas fa-user-circle fa-2x"></i>
            <span>Login or Register</span>
        </div>
        <ul class="drawer-menu">
            <li><a href="#"><i class="fas fa-trophy"></i> Competitions</a></li>
            <li><a href="#"><i class="fas fa-shield-alt"></i> Teams</a></li>
            <li><a href="#"><i class="fas fa-running"></i> Players</a></li>
            <li><a href="#"><i class="fas fa-exchange-alt"></i> Transfers</a></li>
            <li><a href="#"><i class="fas fa-tv"></i> Televised Matches</a></li>
            <div class="drawer-divider"></div>
            <li><a href="#"><i class="fas fa-ban"></i> Remove Ads</a></li>
            <li><a href="#"><i class="fas fa-cog"></i> Settings</a></li>
            <li><a href="#"><i class="fas fa-info-circle"></i> About Us</a></li>
        </ul>
    </div>

    <!-- MAIN VIEWS -->

    <!-- 1. MATCHES TAB -->
    <div id="tab-matches" class="tab-content active">
        <div class="date-bar">
            <span class="date-btn active">YESTERDAY</span>
            <span class="date-btn">TODAY</span>
            <span class="date-btn">LIVE</span>
            <span class="date-btn">TOMORROW</span>
        </div>
        <div id="matches-list">
            <!-- Matches Loaded dynamically -->
            <div class="match-card">
                <div class="league-title">
                    <i class="fas fa-globe"></i> INTERNATIONAL FRIENDLIES
                </div>
                <div class="match-row">
                    <div class="team-side">
                        <i class="fas fa-futbol"></i>
                        <span>Bayern München</span>
                    </div>
                    <span class="score-box">2 - 1</span>
                    <div class="team-side away">
                        <span>Aston Villa</span>
                        <i class="fas fa-futbol"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 2. FAVOURITES TAB -->
    <div id="tab-favourites" class="tab-content">
        <h3 style="margin-bottom:10px;">Most Wanted Teams</h3>
        <div class="fav-grid">
            <div class="fav-item">
                <img src="https://www.thesportsdb.com/images/media/team/badge/small/uvxuqq1448813372.png">
                <div>Arsenal</div>
            </div>
            <div class="fav-item">
                <img src="https://www.thesportsdb.com/images/media/team/badge/small/tyytxu1448813373.png">
                <div>Man Utd</div>
            </div>
            <div class="fav-item">
                <img src="https://www.thesportsdb.com/images/media/team/badge/small/txtrur1448813373.png">
                <div>Man City</div>
            </div>
            <div class="fav-item">
                <img src="https://www.thesportsdb.com/images/media/team/badge/small/0002151522071853.png">
                <div>Real Madrid</div>
            </div>
        </div>
    </div>

    <!-- 3. EXPLORE TAB -->
    <div id="tab-explore" class="tab-content">
        <input type="text" class="search-box" placeholder="Search countries or competitions...">
        <h4 style="margin-bottom:10px; color:#555;">Featured Countries</h4>
        <ul style="list-style:none;">
            <li style="padding:10px; background:white; margin-bottom:5px; border-radius:5px; display:flex; justify-content:space-between;">
                <span>🇪🇹 Ethiopia</span>
                <span style="color:#888;">3 Comps</span>
            </li>
            <li style="padding:10px; background:white; margin-bottom:5px; border-radius:5px; display:flex; justify-content:space-between;">
                <span>🏴󠁧󠁢󠁥󠁮󠁧󠁿 England</span>
                <span style="color:#888;">39 Comps</span>
            </li>
            <li style="padding:10px; background:white; margin-bottom:5px; border-radius:5px; display:flex; justify-content:space-between;">
                <span>🇪🇸 Spain</span>
                <span style="color:#888;">986 Comps</span>
            </li>
        </ul>
    </div>

    <!-- 4. TRANSFERS TAB -->
    <div id="tab-transfers" class="tab-content">
        <h3 style="margin-bottom:10px;">Latest Transfers</h3>
        <div class="news-card">
            <div class="news-content">
                <div class="news-title">J. Correa ➡️ Botafogo to Estudiantes</div>
                <p class="news-desc">Official: Loan deal finalized until June 2025.</p>
            </div>
        </div>
        <div class="news-card">
            <div class="news-content">
                <div class="news-title">M. Kumbulla ➡️ Roma to Rayo Vallecano</div>
                <p class="news-desc">Official: Free transfer completed today.</p>
            </div>
        </div>
    </div>

    <!-- 5. NEWS TAB -->
    <div id="tab-news" class="tab-content">
        <h3 style="margin-bottom:10px;">Featured News</h3>
        <div class="news-card">
            <img src="https://www.thesportsdb.com/images/media/player/thumb/p138371583002237.jpg" alt="News">
            <div class="news-content">
                <div class="news-title">Diomande completes medical test</div>
                <p class="news-desc">Ivorian winger Yan Diomande was pictured ahead of his medical on Friday...</p>
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
            const drawer = document.getElementById('drawer');
            const overlay = document.getElementById('overlay');
            drawer.classList.toggle('active');
            overlay.classList.toggle('active');
        }

        function switchTab(tabId, element) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            // Remove active class from nav items
            document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));

            // Show current tab & activate nav
            document.getElementById('tab-' + tabId).classList.add('active');
            element.classList.add('active');
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
