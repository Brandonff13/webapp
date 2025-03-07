from flask import Flask, jsonify, render_template
import sqlite3
import json
import random
import os

app = Flask(__name__)

DATABASE = 'nobel.db'

def init_db():
    """Crea la base de datos y la tabla si no existen."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS winners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link TEXT,
            name TEXT,
            year INTEGER,
            category TEXT,
            country TEXT,
            born_in TEXT,
            text TEXT,
            date_of_birth TEXT,
            date_of_death TEXT,
            place_of_birth TEXT,
            place_of_death TEXT,
            gender TEXT
        )
    ''')
    conn.commit()
    conn.close()

def populate_db():
    """Carga el archivo JSON y lo inserta en la base de datos si aún está vacío."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM winners')
    count = c.fetchone()[0]
    if count == 0:
        # Asegurarse de que el archivo JSON esté en la misma carpeta
        with open('nwinners_list_clean.json', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                c.execute('''
                    INSERT INTO winners (link, name, year, category, country, born_in, text, date_of_birth, date_of_death, place_of_birth, place_of_death, gender)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('link'),
                    item.get('name'),
                    item.get('year'),
                    item.get('category'),
                    item.get('country'),
                    item.get('born_in'),
                    item.get('text'),
                    item.get('date_of_birth'),
                    item.get('date_of_death'),
                    item.get('place_of_birth'),
                    item.get('place_of_death'),
                    item.get('gender'),
                ))
        conn.commit()
    conn.close()

@app.route('/api/winners', methods=['GET'])
def api_winners():
    """Devuelve 5 premios Nobel en formato JSON."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM winners')
    winners = c.fetchall()
    conn.close()
    # Seleccionar 5 registros aleatorios
    random_winners = random.sample(winners, 5)
    winners_list = []
    for w in random_winners:
        winners_list.append({
            'id': w[0],
            'link': w[1],
            'name': w[2],
            'year': w[3],
            'category': w[4],
            'country': w[5],
            'born_in': w[6],
            'text': w[7],
            'date_of_birth': w[8],
            'date_of_death': w[9],
            'place_of_birth': w[10],
            'place_of_death': w[11],
            'gender': w[12]
        })
    return jsonify(winners_list)

@app.route('/')
def index():
    """
    Consulta la base de datos para agrupar la cantidad de ganadores por país y renderiza
    el template con los datos necesarios para la gráfica.
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT country, COUNT(*) as count FROM winners GROUP BY country')
    data = c.fetchall()
    conn.close()
    countries = [row[0] for row in data]
    counts = [row[1] for row in data]
    return render_template('index.html', countries=countries, counts=counts)

if __name__ == '__main__':
    # Si no existe la base de datos se crea y se carga el JSON
    if not os.path.exists(DATABASE):
        init_db()
        populate_db()
    app.run(debug=True)
