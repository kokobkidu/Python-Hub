from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Koki Score API በስኬት እየሰራ ነው!"})

if __name__ == '__main__':
    app.run()
