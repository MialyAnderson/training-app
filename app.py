from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime, date
import json
import os

app = Flask(__name__)

# Fichier pour sauvegarder les données
DATA_FILE = 'training_data.json'

def load_data():
    """Charge les données depuis le fichier JSON"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'measurements': [],
        'daily_exercises': {},
        'notes': {}
    }

def save_data(data):
    """Sauvegarde les données dans le fichier JSON"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_current_week():
    """Détermine la semaine actuelle du programme (1-6)"""
    # Date de début du programme: 24 juin 2025
    start_date = date(2025, 6, 24)
    today = date.today()
    days_elapsed = (today - start_date).days
    week = (days_elapsed // 7) + 1
    return max(1, min(6, week))

def get_weekly_program(week):
    """Retourne le programme selon la semaine"""
    if week <= 3:
        return {
            'footing': '30-40 min allure modérée',
            'type': 'modéré'
        }
    else:
        return {
            'footing': 'Alternance: 2 jours 40 min modéré / 3 jours fractionné (20-25 min alternance 1 min rapide / 1 min lent)',
            'type': 'mixte'
        }

@app.route('/')
def index():
    """Page d'accueil avec le programme du jour"""
    data = load_data()
    today_str = date.today().isoformat()
    current_week = get_current_week()
    weekly_program = get_weekly_program(current_week)
    
    # Exercices du jour
    today_exercises = data['daily_exercises'].get(today_str, {})
    
    # Date formatée pour l'affichage
    today_display = date.today().strftime('%A %d %B %Y')
    
    return render_template('index.html', 
                         current_week=current_week,
                         weekly_program=weekly_program,
                         today_exercises=today_exercises,
                         today=today_display)

@app.route('/complete_exercise', methods=['POST'])
def complete_exercise():
    """Marque un exercice comme terminé"""
    data = load_data()
    today_str = date.today().isoformat()
    exercise = request.form.get('exercise')
    completed = request.form.get('completed') == 'true'
    
    if today_str not in data['daily_exercises']:
        data['daily_exercises'][today_str] = {}
    
    data['daily_exercises'][today_str][exercise] = completed
    save_data(data)
    
    return jsonify({'success': True})

@app.route('/measurements')
def measurements():
    """Page des mesures"""
    data = load_data()
    today_str = date.today().isoformat()
    return render_template('measurements.html', 
                         measurements=data['measurements'],
                         today=today_str)

@app.route('/add_measurement', methods=['POST'])
def add_measurement():
    """Ajoute une nouvelle mesure"""
    data = load_data()
    
    measurement = {
        'date': request.form.get('date'),
        'weight': float(request.form.get('weight', 0)),
        'waist': float(request.form.get('waist', 0)),
        'notes': request.form.get('notes', '')
    }
    
    data['measurements'].append(measurement)
    save_data(data)
    
    return redirect(url_for('measurements'))

@app.route('/progress')
def progress():
    """Page de suivi des progrès"""
    data = load_data()
    
    # Calcul des statistiques
    total_days = len(data['daily_exercises'])
    completed_sessions = 0
    
    for day_exercises in data['daily_exercises'].values():
        if any(day_exercises.values()):
            completed_sessions += 1
    
    return render_template('progress.html', 
                         total_days=total_days,
                         completed_sessions=completed_sessions,
                         daily_exercises=data['daily_exercises'])

if __name__ == '__main__':
    app.run(debug=True)