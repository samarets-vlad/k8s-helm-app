from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import os

app = Flask(__name__)
CORS(app)

def get_db():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'mysql'),
        user=os.getenv('DB_USER', 'todouser'),
        password=os.getenv('DB_PASSWORD', 'todopassword'),
        database=os.getenv('DB_NAME', 'tododb')
    )

@app.route('/api', methods=['GET'])
def get_tasks():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(tasks)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api', methods=['POST'])
def add_task():
    try:
        data = request.get_json()
        task = data.get('task', '')
        if not task:
            return jsonify({"status": "error", "message": "Task is required"}), 400
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO tasks (title) VALUES (%s)", (task,))
        db.commit()
        task_id = cursor.lastrowid
        cursor.close()
        db.close()
        return jsonify({"status": "success", "id": task_id}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
