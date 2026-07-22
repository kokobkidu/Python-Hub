from flask import Flask, render_template_string, request
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def home():
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    match_id = request.args.get('match_id')
    
    # የሳምንቱን ቀናት ማዘጋጀት
    dates_list = []
    base_date = datetime.now() - timedelta(days=3)
    for i in range(7):
        d = base_date + timedelta(days=i)
        d_str = d.strftime('%Y-%m-%d')
        d_label = d.strftime('%a %d %b')
        dates_list.append({'date': d_str, 'label': d_label})
    
    # ለእያንዳንዱ ቀን የተለዩ እውነተኛ ሊጎች እና ግጥሚያዎች በዕለት (Date-based Database)
    daily_database = {
        # የዛሬ ወይም የተመረጠ ቀን ውሂብ በናሙና መልክ ለእየቀኑ እንከፍላለን
        selected_date: [
            {
                "league": f"🌍 {selected_date} - INTERNATIONAL & LEAGUES",
                "matches": [
                    {"id": f"m_{selected_date}_1", "home": "Team A", "away": "Team B", "h": "1", "a": "0", "status": "FT"},
                    {"id": f"m_{selected_date}_2", "home": "Team C", "away": "Team D", "h": "2", "a": "2", "status": "FT"},
                    {"id": f"m_{selected_date}_3", "home": "Team E", "away": "Team F", "h": "-", "a": "-", "status": "19:30"}
                ]
            },
            {
                "league": "⚽ REGIONAL & LOCAL MATCHES",
                "matches": [
                    {"id": f"m_{selected_date}_4", "home": "Club X", "away": "Club Y", "h": "0", "a": "0", "status": "TIMED"},
                    {"id": f"m_{selected_date}_5", "home": "Club W", "away": "Club Z", "h": "3", "a": "1", "status": "FT"}
                ]
            }
        ]
    }
    
    # የተለየ ቀን ካልተመዘገበ ነባሪ ጨዋታዎች እንዲኖሩት
    current_day_matches = daily_database.get(selected_date, [
        {
            "league": f"📅 MATCHES FOR {selected_date}",
            "matches": [
                {"id": f"def_{selected_date}_1", "home": "Local FC", "away": "City United", "h": "1", "a": "1", "status": "FT"},
                {"id": f"def_{selected_date}_2", "home": "Star Rovers", "away": "Olympic Athletic", "h": "-", "a": "-", "status": "21:00"}
            ]
        }
    ])

    # ማችን ማግኘት ለዲቴል ፔጅ
    all_flat_matches = []
    for group in current_day_matches:
        for m in group['matches']:
            all_flat_matches.append({**m, "league": group['league']})

    if match_id:
        selected_match = next((m for m in all_flat_matches if m['id'] == match_id), None)
        if selected_match:
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Match Details - Koki Score</title>
                <style>
                    body { font-family: Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 0; }
                    .top-bar { background-color: #1b5e20; color: white; padding: 14px; text-align: center; font-size: 18px; font-weight: bold; }
                    .back-btn { display: inline-block; margin: 15px; color: #1b5e20; text-decoration: none; font-weight: bold; }
                    .container { padding: 15px; max-width: 600px; margin: auto; background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
                    .score-header { text-align: center; font-size: 22px; font-weight: bold; color: #1b5e20; margin: 20px 0; background: #e8f5e9; padding: 15px; border-radius: 6px; }
                </style>
            </head>
            <body>
                <div class="top-bar">⚽ Koki Score - Match Detail</div>
                <div style="max-width: 600px; margin: auto;"><a href="/?date={{ date }}" class="back-btn">⬅ ወደ ውጤቶች ተመለስ</a></div>
                <div class="container">
                    <h3>{{ match.league }}</h3>
                    <div class="score-header">
                        {{ match.home }} {{ match.h }} - {{ match.a }} {{ match.away }}
                        <div style="font-size: 12px; color: #666; margin-top: 5px;">ሁኔታ: {{ match.status }}</div>
                    </div>
                </div>
            </body>
            </html>
            """, match=selected_match, date=selected_date)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Koki Score</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f8f9fa; margin: 0; padding: 0; }}
            .top-bar {{ background-color: #1b5e20; color: white; padding: 14px; text-align: center; font-size: 18px; font-weight: bold; }}
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
            .score-box {{ width: 24%; text-align: center; background: #f1f8e9; padding: 6px 4px; border-radius: 6px; font-weight: bold; font-size: 14px; color: #2e7d32; text-decoration: none; display: block; border: 1px solid #dcedc8; }}
            .match-status {{ font-size: 9px; color: #d32f2f; margin-top: 2px; text-transform: uppercase; font-weight: bold; }}
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
    
    for group in current_day_matches:
        html_content += f'<div class="league-title">{group["league"]}</div>'
        for match in group['matches']:
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
            
    html_content += """
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    app.run()
