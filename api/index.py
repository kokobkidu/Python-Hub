from flask import Flask, render_template_string, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def home():
    # ከዩአርኤል የተመረጠውን ቀን መቀበል (ነባሪው የዛሬው ቀን ነው)
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    tab_type = request.args.get('tab', 'today')
    
    # ለምሳሌ በቀናት መካከል ለመቀያየር የሚረዱ ቀኖች
    today_str = datetime.now().strftime('%Y-%m-%d')
    yesterday_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    tomorrow_str = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # የኤፒአይ ጥያቄ በተመረጠው ቀን መሰረት
    url = f"https://v3.football.api-sports.io/fixtures?date={selected_date}"
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': '2569736eeedf66e94d33e0afffa3694a'
    }
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BeSoccer Style - Live Scores</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 0; }}
            .top-bar {{ background-color: #2e7d32; color: white; padding: 12px; text-align: center; font-size: 18px; font-weight: bold; }}
            .tabs {{ display: flex; background-color: #388e3c; overflow-x: auto; white-space: nowrap; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
            .tabs a {{ color: #c8e6c9; padding: 12px 18px; text-decoration: none; font-size: 13px; font-weight: bold; text-transform: uppercase; display: inline-block; }}
            .tabs a.active {{ color: white; border-bottom: 3px solid white; background-color: rgba(255,255,255,0.1); }}
            .container {{ padding: 10px; max-width: 600px; margin: auto; }}
            .league-title {{ font-size: 13px; font-weight: bold; color: #555; margin: 15px 5px 8px 5px; text-transform: uppercase; }}
            .match-card {{ background: white; margin-bottom: 8px; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }}
            .team {{ width: 38%; font-weight: bold; font-size: 13px; color: #333; display: flex; align-items: center; }}
            .team.home {{ justify-content: flex-end; text-align: right; }}
            .team.away {{ justify-content: flex-start; text-align: left; }}
            .team img {{ width: 20px; height: 20px; margin: 0 6px; object-fit: contain; }}
            .score-box {{ width: 24%; text-align: center; background: #f8f9fa; padding: 6px; border-radius: 4px; font-weight: bold; font-size: 15px; color: #2e7d32; border: 1px solid #e0e0e0; }}
            .match-status {{ font-size: 9px; color: #666; margin-top: 3px; text-transform: uppercase; }}
            .no-match {{ text-align: center; padding: 30px; color: #666; font-weight: bold; background: white; border-radius: 8px; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="top-bar">⚽ BESOCCER HUB</div>
        <div class="tabs">
            <a href="/?date={yesterday_str}&tab=yesterday" class="{'active' if tab_type=='yesterday' else ''}">Yesterday</a>
            <a href="/?date={today_str}&tab=today" class="{'active' if tab_type=='today' else ''}">Today</a>
            <a href="/?date={tomorrow_str}&tab=tomorrow" class="{'active' if tab_type=='tomorrow' else ''}">Tomorrow</a>
        </div>
        <div class="container">
    """
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        matches = data.get('response', [])
        
        if matches:
            # ሊጎችን በየራሳቸው ሐጅ (Group) መክፈል ይቻላል፣ ለአሁን በንጽህና እናሳያለን
            current_league = ""
            for match in matches:
                league_name = match['league']['name']
                country = match['league']['country']
                
                if league_name != current_league:
                    current_league = league_name
                    html_content += f'<div class="league-title">🏆 {country}: {current_league}</div>'
                
                home_team = match['teams']['home']['name']
                home_logo = match['teams']['home']['logo']
                
                away_team = match['teams']['away']['name']
                away_logo = match['teams']['away']['logo']
                
                goals = match.get('goals', {})
                home_goals = goals.get('home')
                away_goals = goals.get('away')
                
                status_short = match['fixture']['status']['short']
                elapsed = match['fixture']['status']['elapsed']
                
                if status_short in ['FT', 'AET', 'PEN']:
                    match_status = "FT"
                elif status_short in ['1H', '2H', 'ET', 'P']:
                    match_status = f"{elapsed}'" if elapsed else status_short
                else:
                    match_status = match['fixture']['status']['short'] # ሰዓት ወይም ሌላ ሁኔታ
                
                h_score = home_goals if home_goals is not None else "-"
                a_score = away_goals if away_goals is not None else "-"
                
                html_content += f"""
                <div class="match-card">
                    <div class="team home">
                        <span>{home_team}</span>
                        <img src="{home_logo}" alt="">
                    </div>
                    <div class="score-box">
                        {h_score} - {a_score}
                        <div class="match-status">{match_status}</div>
                    </div>
                    <div class="team away">
                        <img src="{away_logo}" alt="">
                        <span>{away_team}</span>
                    </div>
                </div>
                """
        else:
            html_content += f'<div class="no-match">ለተመረጠው ቀን ({selected_date}) የተመዘገበ ግጥሚያ የለም</div>'
            
    except Exception as e:
        html_content += f'<div class="no-match">ስህተት ተፈጥሯል: {str(e)}</div>'
        
    html_content += """
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    app.run()
