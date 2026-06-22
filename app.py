"""
Mr. Goli Soda Finance - Flask App
CLEAN VERSION
"""

import os
from flask import Flask, render_template, jsonify, request, session
from functools import wraps
import json
from db import cursor, init_db

app = Flask(__name__, static_folder='static', static_url_path='')
app.secret_key = "goli-soda-secret-key-2024"
PW = "SAFC@123"

# Initialize DB
init_db()

# ===== AUTH DECORATOR =====
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({"error": "Not logged in"}), 401
        return f(*args, **kwargs)
    return decorated_function

# ===== AUTH ENDPOINTS =====
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        password = data.get('password')
        
        if password == PW:
            session['user'] = 'admin'
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Wrong password"}), 401
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({"success": True})

@app.route('/api/me', methods=['GET'])
def me():
    if 'user' in session:
        return jsonify({"user": session['user']})
    return jsonify({"error": "Not logged in"}), 401

# ===== CONFIG ENDPOINT =====
@app.route('/api/config', methods=['GET'])
@login_required
def get_config():
    try:
        # Get settings
        with cursor() as cur:
            cur.execute("SELECT * FROM settings WHERE id=1")
            settings = cur.fetchone()
            if not settings:
                settings = {"id": 1, "fee": 0, "budget_limit": 0, "warning": 0}
        
        # Get franchises
        with cursor() as cur:
            cur.execute("SELECT id, name, state FROM franchises ORDER BY id")
            franchises = cur.fetchall()
        
        # Get categories
        with cursor() as cur:
            cur.execute("SELECT id, name FROM categories ORDER BY id")
            categories = cur.fetchall()
        
        return jsonify({
            "settings": settings,
            "franchises": franchises,
            "categories": categories
        })
    except Exception as e:
        print(f"CONFIG ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ===== SETTINGS ENDPOINTS =====
@app.route('/api/settings', methods=['PUT'])
@login_required
def update_settings():
    try:
        data = request.json
        fee = data.get('fee', 0)
        budget_limit = data.get('budget_limit', 0)
        warning = data.get('warning', 0)
        
        with cursor(commit=True) as cur:
            cur.execute("UPDATE settings SET fee=%s, budget_limit=%s, warning=%s WHERE id=1",
                       (fee, budget_limit, warning))
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"UPDATE SETTINGS ERROR: {e}")
        return jsonify({"error": str(e)}), 500

# ===== FRANCHISE ENDPOINTS =====
@app.route('/api/franchises', methods=['POST'])
@login_required
def add_franchise():
    try:
        data = request.json
        name = data.get('name', '').strip()
        state = data.get('state', '').strip()
        
        if not name or not state:
            return jsonify({"error": "Name and state required"}), 400
        
        with cursor(commit=True) as cur:
            cur.execute("INSERT INTO franchises (name, state) VALUES (%s, %s)",
                       (name, state))
            result = cur.fetchone()
        
        if result:
            return jsonify(result), 201
        else:
            return jsonify({"success": True}), 201
    
    except Exception as e:
        print(f"ADD FRANCHISE ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/franchises/<int:fid>', methods=['PUT'])
@login_required
def update_franchise(fid):
    try:
        data = request.json
        name = data.get('name', '').strip()
        state = data.get('state', '').strip()
        
        with cursor(commit=True) as cur:
            cur.execute("UPDATE franchises SET name=%s, state=%s WHERE id=%s",
                       (name, state, fid))
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"UPDATE FRANCHISE ERROR: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/franchises/<int:fid>', methods=['DELETE'])
@login_required
def delete_franchise(fid):
    try:
        with cursor(commit=True) as cur:
            cur.execute("DELETE FROM franchises WHERE id=%s", (fid,))
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"DELETE FRANCHISE ERROR: {e}")
        return jsonify({"error": str(e)}), 500

# ===== CATEGORY ENDPOINTS =====
@app.route('/api/categories', methods=['POST'])
@login_required
def add_category():
    try:
        data = request.json
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({"error": "Name required"}), 400
        
        with cursor(commit=True) as cur:
            cur.execute("INSERT INTO categories (name) VALUES (%s)", (name,))
            result = cur.fetchone()
        
        if result:
            return jsonify(result), 201
        else:
            return jsonify({"success": True}), 201
    
    except Exception as e:
        print(f"ADD CATEGORY ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories/<int:cid>', methods=['PUT'])
@login_required
def update_category(cid):
    try:
        data = request.json
        name = data.get('name', '').strip()
        
        with cursor(commit=True) as cur:
            cur.execute("UPDATE categories SET name=%s WHERE id=%s", (name, cid))
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"UPDATE CATEGORY ERROR: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories/<int:cid>', methods=['DELETE'])
@login_required
def delete_category(cid):
    try:
        with cursor(commit=True) as cur:
            cur.execute("DELETE FROM categories WHERE id=%s", (cid,))
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"DELETE CATEGORY ERROR: {e}")
        return jsonify({"error": str(e)}), 500

# ===== ENTRIES ENDPOINTS =====
@app.route('/api/entries', methods=['GET'])
@login_required
def get_entries():
    try:
        with cursor() as cur:
            cur.execute("SELECT * FROM entries_with_details ORDER BY date DESC")
            entries = cur.fetchall()
        
        return jsonify(entries)
    except Exception as e:
        print(f"GET ENTRIES ERROR: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/entries', methods=['POST'])
@login_required
def add_entry():
    try:
        data = request.json
        edate = data.get('edate')
        franchise_id = data.get('franchise_id')
        category_id = data.get('category_id')
        descr = data.get('descr', '')
        amount = data.get('amount')
        invoice = data.get('invoice', '')
        bill = data.get('bill', 'Yes')
        remarks = data.get('remarks', '')
        
        with cursor(commit=True) as cur:
            cur.execute(
                "INSERT INTO entries (edate, franchise_id, category_id, descr, amount, invoice, bill, remarks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (edate, franchise_id, category_id, descr, amount, invoice, bill, remarks)
            )
            result = cur.fetchone()
        
        if result:
            return jsonify(result), 201
        else:
            return jsonify({"success": True}), 201
    
    except Exception as e:
        print(f"ADD ENTRY ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/entries/<int:eid>', methods=['PUT'])
@login_required
def update_entry(eid):
    try:
        data = request.json
        edate = data.get('edate')
        franchise_id = data.get('franchise_id')
        category_id = data.get('category_id')
        descr = data.get('descr', '')
        amount = data.get('amount')
        invoice = data.get('invoice', '')
        bill = data.get('bill', 'Yes')
        remarks = data.get('remarks', '')
        
        with cursor(commit=True) as cur:
            cur.execute(
                "UPDATE entries SET edate=%s, franchise_id=%s, category_id=%s, descr=%s, amount=%s, invoice=%s, bill=%s, remarks=%s WHERE id=%s",
                (edate, franchise_id, category_id, descr, amount, invoice, bill, remarks, eid)
            )
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"UPDATE ENTRY ERROR: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/entries/<int:eid>', methods=['DELETE'])
@login_required
def delete_entry(eid):
    try:
        with cursor(commit=True) as cur:
            cur.execute("DELETE FROM entries WHERE id=%s", (eid,))
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"DELETE ENTRY ERROR: {e}")
        return jsonify({"error": str(e)}), 500

# ===== IMPORT/EXPORT ENDPOINTS =====
@app.route('/api/import', methods=['POST'])
@login_required
def import_data():
    try:
        data = request.json
        rows = data.get('rows', [])
        clear = data.get('clear', False)
        
        if clear:
            with cursor(commit=True) as cur:
                cur.execute("DELETE FROM entries")
        
        with cursor(commit=True) as cur:
            for row in rows:
                cur.execute(
                    "INSERT INTO entries (edate, franchise_id, category_id, descr, amount, invoice, bill, remarks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (row.get('edate'), row.get('franchise_id'), row.get('category_id'),
                     row.get('descr', ''), row.get('amount'), row.get('invoice', ''),
                     row.get('bill', 'Yes'), row.get('remarks', ''))
                )
        
        return jsonify({"success": True, "count": len(rows)})
    except Exception as e:
        print(f"IMPORT ERROR: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/export.csv', methods=['GET'])
@login_required
def export_data():
    try:
        with cursor() as cur:
            cur.execute("SELECT * FROM entries_with_details ORDER BY date DESC")
            entries = cur.fetchall()
        
        # Build CSV
        csv = "Date,Franchise,State,Category,Description,Amount,Invoice,Bill,Remarks\n"
        for e in entries:
            date = e.get('date', '')
            franchise = e.get('franchise', '')
            state = e.get('state', '')
            cat = e.get('cat', '')
            desc = e.get('desc', '')
            amount = e.get('amount', '')
            invoice = e.get('invoice', '')
            bill = e.get('bill', '')
            remarks = e.get('remarks', '')
            csv += f'"{date}","{franchise}","{state}","{cat}","{desc}","{amount}","{invoice}","{bill}","{remarks}"\n'
        
        return csv, 200, {'Content-Disposition': 'attachment; filename=entries.csv'}
    except Exception as e:
        print(f"EXPORT ERROR: {e}")
        return jsonify({"error": str(e)}), 500

# ===== SERVE HTML =====
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    if path != "" and path != "index.html":
        return app.send_static_file(path)
    return app.send_static_file('index.html')

# ===== RUN =====
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=False)
