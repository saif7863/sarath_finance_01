"""
Mr. Goli Soda Finance - Flask Backend
COMPLETE VERSION - ALL ENDPOINTS
"""

from flask import Flask, render_template, request, jsonify, send_file
from functools import wraps
import json
from db import cursor, init_db
from io import StringIO, BytesIO
import csv
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='')
app.secret_key = 'mr-goli-soda-franchise-finance'
init_db()

PASSWORD = "SAFC@123"
sessions = {}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or auth not in sessions.values():
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

# ===== AUTH =====
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    if data.get('password') != PASSWORD:
        return jsonify({"error": "Invalid password"}), 401
    
    token = f"token_{len(sessions)+1}"
    sessions[token] = token
    return jsonify({"token": token, "auth": True, "user": "Team member"})

@app.route('/api/logout', methods=['POST'])
def logout():
    auth = request.headers.get('Authorization')
    if auth and auth in sessions:
        del sessions[auth]
    return jsonify({"ok": True})

@app.route('/api/me', methods=['GET'])
def me():
    auth = request.headers.get('Authorization')
    if auth and auth in sessions:
        return jsonify({"auth": True, "user": "Team member"})
    return jsonify({"auth": False})

# ===== CONFIG =====
@app.route('/api/config', methods=['GET'])
@login_required
def get_config():
    try:
        # Settings
        with cursor() as cur:
            cur.execute("SELECT * FROM settings WHERE id=1")
            settings = cur.fetchone()
            if not settings:
                settings = {"id": 1, "fee": 0, "budget_limit": 0, "warning": 0}
        
        # Franchises
        with cursor() as cur:
            cur.execute("SELECT * FROM franchises ORDER BY id")
            franchises = cur.fetchall()
        
        # Categories
        with cursor() as cur:
            cur.execute("SELECT * FROM categories ORDER BY id")
            categories = cur.fetchall()
        
        return jsonify({
            "settings": settings,
            "franchises": franchises,
            "categories": categories
        })
    except Exception as e:
        print(f"ERROR in /api/config: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/settings', methods=['PUT'])
@login_required
def update_settings():
    try:
        data = request.json or {}
        with cursor(commit=True) as cur:
            cur.execute(
                "UPDATE settings SET fee=%s, budget_limit=%s, warning=%s WHERE id=1",
                [data.get('fee', 0), data.get('budget_limit', 0), data.get('warning', 0)]
            )
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== ENTRIES =====
@app.route('/api/entries', methods=['GET'])
@login_required
def get_entries():
    try:
        with cursor() as cur:
            cur.execute("SELECT * FROM entries_with_details ORDER BY date DESC")
            entries = cur.fetchall()
        return jsonify(entries)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/entries', methods=['POST'])
@login_required
def create_entry():
    try:
        data = request.json or {}
        with cursor(commit=True) as cur:
            cur.execute(
                "INSERT INTO entries(edate, franchise_id, category_id, descr, amount, invoice, bill, remarks) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                [
                    data.get('edate') or data.get('date'),
                    data.get('franchise_id'),
                    data.get('category_id'),
                    data.get('descr') or data.get('desc'),
                    data.get('amount', 0),
                    data.get('invoice', ''),
                    data.get('bill', 'Yes'),
                    data.get('remarks', '')
                ]
            )
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/entries/<int:id>', methods=['PUT'])
@login_required
def update_entry(id):
    try:
        data = request.json or {}
        with cursor(commit=True) as cur:
            cur.execute(
                "UPDATE entries SET edate=%s, franchise_id=%s, category_id=%s, descr=%s, amount=%s, invoice=%s, bill=%s, remarks=%s WHERE id=%s",
                [
                    data.get('edate') or data.get('date'),
                    data.get('franchise_id'),
                    data.get('category_id'),
                    data.get('descr') or data.get('desc'),
                    data.get('amount', 0),
                    data.get('invoice', ''),
                    data.get('bill', 'Yes'),
                    data.get('remarks', ''),
                    id
                ]
            )
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/entries/<int:id>', methods=['DELETE'])
@login_required
def delete_entry(id):
    try:
        with cursor(commit=True) as cur:
            cur.execute("DELETE FROM entries WHERE id=%s", [id])
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== FRANCHISES =====
@app.route('/api/franchises', methods=['POST'])
@login_required
def create_franchise():
    try:
        data = request.json or {}
        with cursor(commit=True) as cur:
            cur.execute(
                "INSERT INTO franchises(name, state) VALUES(%s,%s)",
                [data.get('name'), data.get('state')]
            )
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/franchises/<int:id>', methods=['PUT'])
@login_required
def update_franchise(id):
    try:
        data = request.json or {}
        with cursor(commit=True) as cur:
            cur.execute(
                "UPDATE franchises SET name=%s, state=%s WHERE id=%s",
                [data.get('name'), data.get('state'), id]
            )
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/franchises/<int:id>', methods=['DELETE'])
@login_required
def delete_franchise(id):
    try:
        with cursor(commit=True) as cur:
            cur.execute("DELETE FROM franchises WHERE id=%s", [id])
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== CATEGORIES =====
@app.route('/api/categories', methods=['POST'])
@login_required
def create_category():
    try:
        data = request.json or {}
        with cursor(commit=True) as cur:
            cur.execute(
                "INSERT INTO categories(name) VALUES(%s)",
                [data.get('name')]
            )
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories/<int:id>', methods=['PUT'])
@login_required
def update_category(id):
    try:
        data = request.json or {}
        with cursor(commit=True) as cur:
            cur.execute(
                "UPDATE categories SET name=%s WHERE id=%s",
                [data.get('name'), id]
            )
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories/<int:id>', methods=['DELETE'])
@login_required
def delete_category(id):
    try:
        with cursor(commit=True) as cur:
            cur.execute("DELETE FROM categories WHERE id=%s", [id])
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== EXPORT/IMPORT =====
@app.route('/api/export.csv', methods=['GET'])
@login_required
def export_csv():
    try:
        with cursor() as cur:
            cur.execute("SELECT * FROM entries_with_details ORDER BY date DESC")
            entries = cur.fetchall()
        
        output = StringIO()
        fieldnames = ['id', 'date', 'franchise', 'state', 'cat', 'desc', 'amount', 'invoice', 'bill', 'remarks']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for e in entries:
            if isinstance(e, dict):
                writer.writerow({k: e.get(k, '') for k in fieldnames})
        
        mem = BytesIO()
        mem.write(output.getvalue().encode('utf-8'))
        mem.seek(0)
        
        return send_file(mem, mimetype='text/csv', as_attachment=True, download_name='entries.csv')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/import', methods=['POST'])
@login_required
def import_entries():
    try:
        data = request.json or {}
        entries_to_add = data.get('entries', [])
        
        with cursor(commit=True) as cur:
            for e in entries_to_add:
                cur.execute(
                    "INSERT INTO entries(edate, franchise_id, category_id, descr, amount, invoice, bill, remarks) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                    [e.get('edate'), e.get('franchise_id'), e.get('category_id'), e.get('descr'), e.get('amount'), e.get('invoice'), e.get('bill'), e.get('remarks')]
                )
        
        return jsonify({"ok": True, "count": len(entries_to_add)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== STATIC =====
@app.route('/', methods=['GET'])
def index():
    return send_file('static/index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
