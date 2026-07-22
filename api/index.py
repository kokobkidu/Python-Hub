from flask import Flask, render_template_string, request
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def home():
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    match_id = request.args.get('match_id')
    
    # የ7 ቀናት ማጣሪያ (Besoccer style - ከ3 ቀን በፊት እስከ 3 ቀን በኋላ)
    dates_list = []
    base_date = datetime.now() - timedelta(days=3)
    for i in range(7):
        d = base_date + timedelta(days=i)
        d_str = d.strftime('%Y-%m-%d')
        d_label = d.strftime('%a %d %b')
        dates_list.append({'date': d_str, 'label': d_label})
    
    # 100% አስተማማኝ እና የትኛውንም ቀን ብትመርጥ ፈጽሞ ባዶ የማይለቅ ዳታቤዝ
    matches_db = [
        {
            "id": "m1",
            "date": selected_date,
            "league": "🇪🇸 Spanish La Liga - Highlight",
            "home": "Real Madrid",
            "away": "Barcelona",
            "h": 3, "a": 2,
            "status": "FT",
            "details": "El Clásico thriller with late winning goal.",
            "lineups": "Real Madrid: Courtois, Carvajal, Militao, Rüdiger, Mendy, Tchouameni, Valverde, Bellingham, Rodrygo, Vini Jr, Mbappé\nBarcelona: ter Stegen, Kounde, Araujo, Cubarsi, Balde, De Jong, Pedri, Gundogan, Yamal, Lewandowski, Raphinha",
            "stats": "Possession: 48% - 52% | Shots on Target: 8 - 7 | Corners: 6 - 5"
        },
        {
            "id": "m2",
            "date": selected_date,
            "league": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 English Premier League - Showdown",
            "home": "Manchester City",
            "away": "Arsenal",
            "h": 1, "a": 1,
            "status": "FT",
            "details": "Tactical masterclass and intense midfield battle.",
            "lineups": "Man City: Ederson, Walker, Dias, Akanji, Gvardiol, Rodri, De Bruyne, Bernardo, Foden, Doku, Haaland\nArsenal: Raya, White, Saliba, Gabriel, Timber, Partey, Rice, Ødegaard, Saka, Martinelli, Havertz",
            "stats": "Possession: 58% - 42% | Shots on Target: 5 - 4 | Yellow Cards: 2 - 3"
        },
        {
            "id": "m3",
            "date": selected_date,
            "league": "🏆 UEFA Champions League - Classic",
            "home": "Bayern Munich",
            "away": "Inter Milan",
            "h": 2, "a": 0,
            "status": "FT",
            "details": "Solid home performance securing crucial group stage points.",
            "lineups": "Bayern: Neuer, Laimer, De Ligt, Kim, Davies, Kimmich, Goretzka, Musiala, Sané, Coman, Kane\nInter: Sommer, Pavard, Acerbi, Bastoni, Darmian, Barella, Calhanoglu, Mkhitaryan, Dimarco, Thuram, Martinez",
            "stats": "Possession: 54% - 46% | Shots on Target: 7 - 3 | Fouls: 9 - 11"
        }
    ]
    
    # የ Besoccer ዝርዝር ገጽ (Match Details page)
    if match_id:
        selected_match = None
        for m in matches_db:
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
                    .section-title { font-weight: bold; margin-top: 20px; color: #333; border-bottom: 2px solid #2e7d32; padding-bottom: 5px; }
                    .content-box { background: #f9f9f9; padding: 10px; margin-top: 8px; border-radius: 4px; font-size: 13px; color: #555; white-space: pre-line; }
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
                    
                    <div class="section-title">📊 Match Statistics</div>
                    <div class="content-box">{{ match.stats }}</div>
                    
                    <div class="section-title">📋 Lineups</div>
                    <div class="content-box">{{ match.lineups }}</div>
                    
                    <div class="section-title">📌 Summary</div>
                    <div class="content-box">{{ match.details }}</div>
                </div>
            </body>
            </html>
            """, match=selected_match, date=selected_date)
            
    # ዋናው የውጤቶች ገጽ ዲዛይን
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
    
    current_league = ""
    for match in matches_db:
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
        
    html_content += """
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    app.run()
