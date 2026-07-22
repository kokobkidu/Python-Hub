from flask import Flask, render_template_string, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# የተሻሻለ ነጻ API ወይም ሰፊ አማራጭ እንጠቀማለን
# አሁን ከፍ ያለ ሊግ ድጋፍ ላለው ነጻ ፖይንት እናስተካክለዋለን
API_KEY = "276477041ca34aa6924720392f56415d"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_KEY}

@app.route('/')
def home():
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # የሳምንቱን ቀናት ማዘጋጀት
    dates_list = []
    base_date = datetime.now() - timedelta(days=2)
    for i in range(6):
        d = base_date + timedelta(days=i)
        d_str = d.strftime('%Y-%m-%d')
        d_label = d.strftime('%a %d %b')
        dates_list.append({'date': d_str, 'label': d_label})
    
    matches = []
    try:
        # ለተመረጠው ቀን ብቻ ሳይሆን አጠቃላይ ያሉትን ጨዋታዎች ለመጎብኘት
        url = f"{BASE_URL}/matches?date={selected_date}"
        response = requests.get(url, headers=HEADERS, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            for m in data.get('matches', []):
                competition = m.get('competition', {})
                competition_name = competition.get('name', 'League')
                area_name = competition.get('area', {}).get('name', '')
                league_display = f"{area_name} - {competition_name}" if area_name else competition_name
                
                home_team = m.get('homeTeam', {}).get('shortName') or m.get('homeTeam', {}).get('name', 'Home')
                away_team = m.get('awayTeam', {}).get('shortName') or m.get('awayTeam', {}).get('name', 'Away')
                
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
                    "status": status
                })
        
        # ተጨማሪ ሊጎች ከሌሉ በዛ ቀን ባለው አማራጭ እንዲሞላ
        if not matches:
            # ሌላ ነጻ Endpoint ዳታ ለመጥራት (ለምሳሌ የዛሬ ግጥሚያዎች በቀጥታ)
            all_matches_url = f"{BASE_URL}/matches"
            resp_all = requests.get(all_matches_url, headers=HEADERS, timeout=5)
            if resp_all.status_code == 200:
                all_data = resp_all.json()
                for m in all_data.get('matches', []):
                    match_date = m.get('utcDate', '').split('T')[0]
                    if match_date == selected_date:
                        comp = m.get('competition', {})
                        matches.append({
                            "id": str(m.get('id')),
                            "league": f"{comp.get('area', {}).get('name', '')} - {comp.get('name', 'League')}",
                            "home": m.get('homeTeam', {}).get('name', 'Home'),
                            "away": m.get('awayTeam', {}).get('name', 'Away'),
                            "h": m.get('score', {}).get('fullTime', {}).get('home', '-'),
                            "a": m.get('score', {}).get('fullTime', {}).get('away', '-'),
                            "status": m.get('status', 'SCHEDULED')
                        })
                        
    except Exception as e:
        print("Error fetching data:", e)

    # ዩአይ (UI) ክፍሉን ይበልጥ ማራኪ እና ንጹህ ማድረግ
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Koki Score</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f8f9fa; margin: 0; padding: 0; }}
            .top-bar {{ background-color: #1b5e20; color: white; padding: 14px; text-align: center; font-size: 18px; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
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
            .score-box {{ width: 22%; text-align: center; background: #f1f8e9; padding: 6px 4px; border-radius: 6px; font-weight: bold; font-size: 14px; color: #2e7d32; border: 1px solid #dcedc8; }}
            .match-status {{ font-size: 9px; color: #d32f2f; margin-top: 2px; text-transform: uppercase; font-weight: bold; }}
            .no-match {{ text-align: center; padding: 40px 20px; color: #6c757d; font-weight: 500; background: white; border-radius: 8px; margin-top: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
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
    
    if matches:
        current_league = ""
        for match in matches:
            if match['league'] != current_league:
                current_league = match['league']
                html_content += f'<div class="league-title">{current_league}</div>'
                
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
        html_content += f'<div class="no-match">በዚህ ቀን ({selected_date}) የተመዘገቡ ግጥሚያዎች የሉም ወይም በነጻው አማራጭ ውስጥ አልተካተቱም።</div>'
        
    html_content += """
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    app.run()
