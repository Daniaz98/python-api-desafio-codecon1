from flask import Flask, request, jsonify
from collections import defaultdict
import json
import os
import time
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

users_db = []

users_count = defaultdict(int)

@app.route("/")
def hello():
    return "Hello universe!"

@app.route("/users", methods=["POST"])
def post_users():
    if 'file' not in request.files:
        return jsonify({
            "response": {
                "status": 400,
                "body": {"message": "Nenhum arquivo enviado", "user_count": 0}
            }
        }), 400 
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Arquivo sem nome'}), 400
    
    if not file.filename.endswith('.json'):
        return jsonify({'error': 'Arquivo não é um json'}), 400
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    total_users = extract_users(file_path)

    return jsonify({
        "response": {
            "status": 200,
            "body": {
                "message": "Arquivo recebido com sucesso",
                "user_count": total_users
            }
        }
    })

def extract_users(file_path):
    count = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        users = json.load(f)
        for user in users:
            name = user.get("name", "").title()
            if name:
                users_count[name] += 1
                count += 1
    return count


@app.route("/superusers", methods=["GET"])
def get_superusers():
    start_time = time.time()
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Arquivo sem nome'}), 400
    
    dt = datetime.now()

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    get_users = get_all_superusers(file_path)

    end_time = time.time()
    duration = f"{round((end_time - start_time) * 1000, 2)} ms"

    return jsonify({
        "response": {
            "status": 200,
            "body": {
                "execution_time_ms": duration,
                "timestamp": dt,
                "data": get_users   
            }
        }
    })

def get_all_superusers(file_path):
    super_users = []

    with open(file_path, 'r', encoding='utf-8') as f:    
        users = json.load(f)
        for user in users:
            score = user.get("score", 0)
            if score >= 900:
                super_users.append(user)

        
    return super_users
    
@app.route("/top-countries", methods=["POST"])
def get_top_countries():
    start_time = time.time()
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Arquivo sem nome'}), 400
    
    dt = datetime.now().isoformat()

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    get_topcountries = get_top_countries_by_users(file_path)

    end_time = time.time()
    duration = f"{round((end_time - start_time) * 1000, 2)} ms"

    return jsonify({
        "response": {
            "status": 200,
            "body": {
                "execution_time_ms": duration,
                "timestamp": dt,
                "countries": get_topcountries  
            }
        }
    })

def get_top_countries_by_users(file_path):
    country_counter = defaultdict(int)

    with open(file_path, 'r', encoding='utf-8') as f:
        users = json.load(f)

        for user in users:
            score = user.get("score", 0)
            if isinstance(score, str):
                try:
                    score = float(score)
                except ValueError:
                    continue


            if score >= 900:
                country = user.get("country", "").strip().title()
                if country:
                    country_counter[country] += 1

    top_countries = sorted(country_counter.items(), key=lambda item: item[1], reverse=True)[:5]

    top_countries_dict = [{"country": c, "total": n} for c, n in top_countries]

    return top_countries_dict


@app.route("/team-insights", methods=["GET"])
def get_team_insights():
    start_time = time.time()
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Arquivo sem nome'}), 400
    
    dt = datetime.now().isoformat()

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    team_data = team_in_data(file_path)

    end_time = time.time()
    duration = f"{round((end_time - start_time) * 1000, 2)} ms"

    return jsonify({
        "response": {
            "status": 200,
            "body": {
                "execution_time_ms": duration,
                "timestamp": dt,
                "teams": team_data
            }
        }
    })

def team_in_data(file_path):
    team_projects = defaultdict(int)

    with open(file_path, 'r', encoding='utf-8') as f:
        users = json.load(f)

        for user in users:
            team = user.get("team", {})
            team_name = user.get("name", "").strip()

            projects = team.get("projects", [])
            completed_count = sum(1 for p in projects if p.get("completed") is True)

        if team_name:
            team_projects[team_name] += completed_count

    result = [{"team": name, "completed_projects": total} for name, total in team_projects.items()]

    result.sort(key=lambda x: x["completed_projects"], reverse=True)

    return result


if __name__ == "__main__":
    app.run(debug=True)

