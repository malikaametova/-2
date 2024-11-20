
from flask import Flask, request, jsonify
import sqlite3
import json

app = Flask(__name__)

DATABASE = 'history.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_table(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            data TEXT NOT NULL
        )
    ''')
    conn.commit()

def init_db():
    conn = get_db_connection()
    create_table(conn)
    conn.close()

# Endpoint для записи событий (POST)
@app.route('/events', methods=['POST'])
def add_event():
    try:
        conn = get_db_connection()
        data = request.get_json()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO history (event, timestamp, data) VALUES (?, ?, ?)",
                         (data['event'], data['timestamp'], json.dumps(data['data'])))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Event added successfully'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    except KeyError as e:
        return jsonify({'error': f"Missing key in request body: {e}"}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint для чтения событий (GET)
@app.route('/events', methods=['GET'])
def get_events():
    try:
        conn = get_db_connection()
        events = conn.execute("SELECT * FROM history").fetchall()
        conn.close()
        return jsonify([dict(row) for row in events])
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db() # Инициализируем базу данных при запуске
    app.run(debug=True, port=5000)
