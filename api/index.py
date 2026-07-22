
from flask import Flask, render_template_string, request
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def home():
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    match_id = request.args.get('match_id')
    
    # የ7 ቀናት ማጣሪያ (Besoccer style)
    dates_list = []
    base_date = datetime.now() - timedelta(days=3)
    for i in range(7):
        d = base_date + timedelta(days=i)
        d_str = d.strftime('%Y-%m-%d')
        d_label = d.strftime('%a %d %b')
        dates_list.append({'date': d_str, 'label': d_label})
    
    # 100% የተሟላ መረጃ (ቅያሬዎችን በአማርኛ ማብራሪያ የያዘ)
    master_matches_db = {
        (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'): [
            {
                "id": "d3-1",
                "league": "🌍 International Friendly Matches",
                "home": "Brazil", "away": "Senegal",
                "h": 2, "a": 4, "status": "FT",
                "scorers": "⚽ H. Diallo 22', 58', S. Mané 45+1', 84' | ⚽ Lucas Paquetá 11', Marquinhos 50'",
                "cards": "🟟 Yellow Cards: I. Jakobs (Senegal) 34', Eder Militão (Brazil) 71'",
                "subs": "🔄 የተደረጉ ቅያሬዎች:\n• ሴኔጋል፦ ኤን. ጃክሰን ገባ | ኤች. ዲያሎ ወጣ\n• ብራዚል፦ ሪቻርሊሶን ገባ | ሮድሪጎ ወጣ",
                "stats": "Possession: 51% - 49% | Shots: 12 - 15 | Fouls: 11 - 13"
            }
        ],
        (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'): [
            {
                "id": "d2-1",
                "league": "🇪🇸 Spanish La Liga - Classic Fixture",
                "home": "Atletico Madrid", "away": "Sevilla",
                "h": 3, "a": 1, "status": "FT",
                "scorers": "⚽ A. Griezmann 15', 72', A. Morata 40' | ⚽ Y. En-Nesyri 55'",
                "cards": "🟟 Yellow Cards: Koke 25', 🟨🟥 Red Card: Koke (Atletico) 88' (2nd Yellow)",
                "subs": "🔄 የተደረጉ ቅያሬዎች:\n• አትሌቲኮ ማድሪድ፦ ممፊስ ዲፓይ ገባ | አልቫሮ ሞራታ ወጣ\n• ሴቪያ፦ ኦካምፖስ ገባ | ሉኬባኪዮ ወጣ",
                "stats": "Possession: 53% - 47% | Shots: 14 - 9 | Corners: 6 - 3"
            }
        ],
        (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'): [
            {
                "id": "d1-1",
                "league": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 English Premier League - High Intensity",
                "home": "Liverpool", "away": "Newcastle United",
                "h": 2, "a": 1, "status": "FT",
                "scorers": "⚽ D. Núñez 85', 90+3' | ⚽ A. Gordon 25'",
                "cards": "🟟 Yellow Cards: W. Endo 40', B. Guimarães 62'",
                "subs": "🔄 የተደረጉ ቅያሬዎች:\n• ሊቨርፑል፦ ዳርዊን ኑኔዝ ገባ | ሉዊስ ዲያዝ ወጣ\n• ኒውካስል፦ ካልום ዊልሰን ገባ | አሌክሳንደር ኢሳክ ወጣ",
                "stats": "Possession: 60% - 40% | Shots on Target: 9 - 4 | Fouls: 10 - 14"
            }
        ],
        datetime.now().strftime('%Y-%m-%d'): [
            {
                "id": "today-1",
                "league": "🏆 UEFA Champions League - Qualifiers",
                "home": "Fenerbahce", "away": "Lugano",
                "h": 2, "a": 1, "status": "FT",
                "scorers": "⚽ E. Džeko 45+2', 46' | ⚽ M. Hajdari 7'",
                "cards": "🟟 Yellow Cards: D. Tadic 30', S. Szymanski 65'",
                "subs": "🔄 የተደረጉ ቅያሬዎች:\n• ፍነርባህቼ፦ ጄንጊዝ ኡንደር ገባ | ዱሻን ታዲች ወጣ\n• ሉጋኖ፦ ቦት ሃይ ገባ | ማቲያ ሃጅዳሪ ወጣ",
                "stats": "Possession: 58% - 42% | Shots: 18 - 8 | Corners: 7 - 2"
            }
        ],
        (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'): [
            {
                "id": "p1-1",
                "league": "🤝 Club International Friendlies",
                "home": "AC Milan", "away": "Chelsea",
                "h": "-", "a": "-", "status": "8:00 PM",
                "scorers": "Upcoming Match",
                "cards": "No cards yet",
                "subs": "🔄 ቅያሬዎች ገና አልተደረጉም (ጨዋታው ገና አልጀመረም)",
                "stats": "Pre-match analysis"
            }
        ],
        (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'): [
            {
                "id": "p2-1",
                "league": "🇩🇪 German Bundesliga - Preview",
                "home": "Borussia Dortmund", "away": "RB Leipzig",
                "h": "-", "a": "-", "status": "6:30 PM",
                "scorers": "Upcoming Match",
                "cards": "No cards",
                "subs": "🔄 ቅያሬዎች ገና አልተደረጉም",
                "stats": "Bundesliga preview"
            }
        ],
        (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'): [
            {
                "id": "p3-1",
                "league": "🇮🇹 Italian Serie A - Preview",
                "home": "Napoli", "away": "Lazio",
                "h": "-", "a": "-", "status": "9:45 PM",
                "scorers": "Upcoming Match",
                "cards": "No cards",
                "subs": "🔄 ቅያሬዎች ገና አልተደረጉም",
                "stats": "Serie A preview"
            }
        ]
    }
    
    matches = master_matches_db.get(selected_date, [])
    
    if match_id:
        selected_match = None
        for m in matches:
            if m['id'] == match_id:
                selected_match = m
                break
                
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
                    .top-bar { background-color: #2e7d32; color: white; padding: 12px; text-align: center; font-size: 19px; font-weight: bold; }
                    .back-btn { display: inline-block; margin: 15px; color: #2e7d32; text-decoration: none; font-weight: bold; }
                    .container { padding: 15px; max-width: 600px; margin: auto; background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
                    .score-header { text-align: center; font-size: 22px; font-weight: bold; color: #2e7d32; margin: 20px 0; background: #e8f5e9; padding: 15px; border-radius: 6px; }
                    .section-title { font-weight: bold; margin-top: 20px; color: #333; border-bottom: 2px solid #2e7d32; padding-bottom: 5px; font-size: 13px; }
                    .content-box { background: #f9f9f9; padding: 10px; margin-top: 8px; border-radius: 4px; font-size: 13px; color: #555; white-space: pre-line; line-height: 1.5; }
                </style>
            </head>
            <body>
                <div class="top-bar">⚽ Koki Score - Match Detail</div>
                <div style="max-width: 600px; margin: auto;">
                    <a href="/?date={{ date }}" class="back-btn">⬅ Back to Scores</a>
                </div>
                <div class="container">
                    <h3>{{ match.league }}</h3>
                    <div class="score-header">
                        {{ match.home }} {{ match.h }} - {{ match.a }} {{ match.away }}
                        <div style="font-size: 12px; color: #666; margin-top: 5px;">Status: {{ match.status }}</div>
                    </div>
                    
                    <div class="section-title">⚽ Goals & Scorers (ጎል ያስቆጠሩት)</div>
                    <div class="content-box">{{ match.scorers }}</div>
                    
                    <div class="section-title">🟨 Red & Yellow Cards (ካርዶች)</div>
                    <div class="content-box">{{ match.cards }}</div>
                    
                    <div class="section-title">🔄 Substitutions (ማን ወጣ / ማን ገባ)</div>
                    <div class="content-box">{{ match.subs }}</div>
                    
                    <div class="section-title">📊 Match Statistics (የጨዋታው ሂደት)</div>
                    <div class="content-box">{{ match.stats }}</div>
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
            
            .score-box {{ width: 24%; text-align: center; background: #e8f5e9; padding: 6px; border-radius: 4px; font-weight: bold; font-size: 15px; color: #2e7d32; border: 1px solid #c8e6c9; text-decoration: none; display: block; transition: 0.2s; }}
            .score-box:hover {{ background: #c8e6c9; }}
            .match-status {{ font-size: 9px; color: #666; margin-top: 3px; text-transform: uppercase; }}
            .no-match {{ text-align: center; padding: 30px; color: #666; font-weight: bold; background: white; border-radius: 8px; margin-top: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
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
                <a href="/?date={selected_date}&match_id={match['id']}" class="score-box">
                    {match['h']} - {match['a']}
                    <div class="match-status">{match['status']}</div>
                </a>
                <div class="team away"><span>{match['away']}</span></div>
            </div>
            """
    else:
        html_content += f'<div class="no-match">ለተመረጠው ቀን ({selected_date}) የተመዘገበ ግጥሚያ የለም።</div>'
        
    html_content += """
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    app.run()
