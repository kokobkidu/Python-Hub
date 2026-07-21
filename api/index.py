from flask import Flask
import requests

app = Flask(__name__)

@app.route('/')
def home():
    url = "https://v3.football.api-sports.io/fixtures?league=39&season=2023"
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': '2569736eeedf66e94d33e0afffa3694a'
    }
    
    try:
        response = requests.get(url, headers=headers)
        # አጠቃላይ መረጃውን እንደ ጽሁፍ እናሳይህ
        return f"የተመለሰው መረጃ: {response.text[:500]}"
        
    except Exception as e:
        return f"ስህተት ተፈጥሯል: {str(e)}"

if __name__ == '__main__':
    app.run()
