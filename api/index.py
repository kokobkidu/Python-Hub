from flask import Flask, render_template_string, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def home():
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # የ7 ቀናት ማጣሪያ (Besoccer style)
    dates_list = []
    base_date = datetime.now() - timedelta(days=3)
    for i in range(7):
        d = base_date + timedelta(days=i)
        d_str = d.strftime('%Y-%m-%d')
        d_label = d.strftime('%a %d %b')
        dates_list.append({'date': d_str, 'label': d_label})
    
    # 100% እውነተኛውን ዳታ ከ API-Football የሚጠራው ኮድ
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
        <title>Koki Score</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 0; }}
            .top-bar {{ background-color: #2e7d32; color: white; padding: 12px; text-align: center; font-size: 19px; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            
            .date-tabs {{ display: flex; background-color: #388e3c; overflow-x: auto; white-space: nowrap; scrollbar-width: none; }}
            .date-tabs::-webkit-scrollbar {{ display: none; }}
            .date-tab {{ color: #c8e6c9; padding: 12px 16px; text-decoration: none; font-size: 12px; font-weight: bold; text-align: center; display: inline-block; border-bottom: 3px solid transparent; }}
            .date-tab.active {{ color: white; border-bottom: 3px solid white; background-color: rgba(255,255,255,0.15); }}
            
            .container {{ padding: 10px; max-width: 600px; margin: auto; }}
            .league-title {{ font-size: 12px; font-weight: bold; color: #333; margin: 15px 5px 6px 5px; text-transform: uppercase; background: #e0e0e0; padding: 6px 10px; border-radius: 4px; }}
            
            .match-card {{ background: white; margin-bottom: 8px; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }}
            .team {{ width: 38%; font-weight: bold; font-size: 13px; color: #333; display: flex; align-items: center; }}
            .team.home {{ justify-content: flex-end; text-align: right; }}
            .team.away {{ justify-content: flex-start; text-align: left; }}
            .team img {{ width: 18px; height: 18px; margin: 0 6px; object-fit: contain; }}
            
            .score-box {{ width: 24%; text-align: center; background: #e8f5e9; padding: 6px; border-radius: 4px; font-weight: bold; font-size: 15px; color: #2e7d32; border: 1px solid #c8e6c9; }}
            .match-status {{ font-size: 9px; color: #666; margin-top: 3px; text-transform: uppercase; }}
            .no-match {{ text-align: center; padding: 30px; color: #555; font-weight: bold; background: white; border-radius: 8px; margin-top: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
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
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        matches = data.get('response', [])
        
        if matches:
            current_league = ""
            for match in matches:
                league_name = match['league']['name']
                country = match['league']['country']
                
                league_header = f"{country}: {league_name}"
                if league_header != current_league:
                    current_league = league_header
                    html_content += f'<div class="league-title">🏆 {current_league}</div>'
                
                home_team = match['teams']['home']['name']
                home_logo = match['teams']['home']['logo']
                
                away_team = match['teams']['away']['name']
                away_logo = match['teams']['away']['logo']
                
                goals = match.get('goals', {})
                home_goals = goals.get('home')
                away_goals = goals.get('away')
                
                status_short = match['fixture']['status']['short']
                elapsed = match['fixture']['status']['elapsed']
                match_time = match['fixture']['date'][11:16]
                
                if status_short in ['FT', 'AET', 'PEN']:
                    match_status = "FT"
                elif status_short in ['1H', '2H', 'ET', 'P']:
                    match_status = f"{elapsed}'" if elapsed else status_short
                elif status_short in ['NS', 'TBD']:
                    match_status = match_time
                else:
                    match_status = status_short
                
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
            html_content += f'<div class="no-match">ለተመረጠው ቀን ({selected_date}) ከእውነተኛው የፉትቦል ሰርቨር የተመዘገበ ግጥሚያ የለም።</div>'
            
    except Exception as e:
        html_content += f'<div class="no-match">የኔትወርክ ወይም የሰርቨር ስህተት አጋጥሟል: {str(e)}</div>'
        
    html_content += """
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    app.run()
