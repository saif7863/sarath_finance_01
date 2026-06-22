"""
Mr. Goli Soda Finance - Flask Backend
Ready to run! No setup needed!
"""

import os
import io
import csv
import time
from functools import wraps
from flask import Flask, request, jsonify, session, send_from_directory, Response
import db

# Initialize Flask
app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = "goli-soda-secret-key-2024"
app.permanent_session_lifetime = 60 * 60 * 24 * 30

# Login credentials
PW = "SAFC@123"
ADMIN_PW = None

# Track login attempts
_tries = {}

# SQL query
ENTRY_SELECT = """
  SELECT e.id, to_char(e.edate,'YYYY-MM-DD') AS date, e.franchise_id, f.name AS franchise,
         f.state, e.category_id, c.name AS cat, e.descr AS "desc", e.amount::float8 AS amount,
         e.invoice, e.bill, e.remarks
  FROM entries e JOIN franchises f ON f.id=e.franchise_id JOIN categories c ON c.id=e.category_id
"""


# ============================================================================
# DECORATORS
# ============================================================================

def login_required(f):
    @wraps(f)
    def w(*a, **k):
        if not session.get("auth"):
            return jsonify(error="Not logged in"), 401
        return f(*a, **k)

    return w


# ============================================================================
# AUTHENTICATION
# ============================================================================

@app.post("/api/login")
def login():
    """Login with password"""
    ip = request.remote_addr or "x"
    now = time.time()
    attempt = _tries.get(ip, {"n": 0, "until": 0})

    if attempt["until"] > now:
        return jsonify(error="Too many attempts"), 429

    if (request.json or {}).get("password", "") == PW:
        _tries.pop(ip, None)
        session.permanent = True
        session["auth"] = True
        return jsonify(ok=True)

    attempt["n"] += 1
    if attempt["n"] >= 6:
        attempt["until"] = now + 300
        attempt["n"] = 0
    _tries[ip] = attempt

    return jsonify(error="Wrong password"), 401


@app.post("/api/logout")
def logout():
    """Logout"""
    session.clear()
    return jsonify(ok=True)


@app.get("/api/me")
def me():
    """Check auth status"""
    return jsonify(auth=bool(session.get("auth")))


# ============================================================================
# CONFIG
# ============================================================================

@app.get("/api/config")
@login_required
def get_config():
    """Get settings, franchises, categories"""
    with db.cursor() as cur:
        cur.execute("SELECT fee::float8 fee, budget_limit::float8 lim, warning::float8 warn FROM settings WHERE id=1")
        s = cur.fetchone()
        cur.execute("SELECT id, name, state FROM franchises ORDER BY id")
        fr = cur.fetchall()
        cur.execute("SELECT id, name FROM categories ORDER BY id")
        cats = cur.fetchall()

    return jsonify(
        fee=s["fee"] if s else 0,
        limit=s["lim"] if s else 0,
        warning=s["warn"] if s else 0,
        franchises=fr,
        categories=cats
    )


@app.put("/api/settings")
@login_required
def put_settings():
    """Update settings"""
    b = request.json or {}
    with db.cursor(commit=True) as cur:
        cur.execute(
            "UPDATE settings SET fee=%s, budget_limit=%s, warning=%s WHERE id=1",
            (b.get("fee") or 0, b.get("limit") or 0, b.get("warning") or 0)
        )
    return jsonify(ok=True)


# ============================================================================
# FRANCHISES
# ============================================================================

@app.post("/api/franchises")
@login_required
def add_franchise():
    """Add franchise"""
    b = request.json or {}
    name = (b.get("name") or "").strip()
    state = (b.get("state") or "").strip()

    if not name:
        return jsonify(error="Name required"), 400

    with db.cursor(commit=True) as cur:
        cur.execute("SELECT 1 FROM franchises WHERE LOWER(name)=LOWER(%s)", (name,))
        if cur.fetchone():
            return jsonify(error="Already exists"), 409
        cur.execute("INSERT INTO franchises(name, state) VALUES (%s, %s) RETURNING id", (name, state))
        return jsonify(id=cur.fetchone()["id"])


@app.put("/api/franchises/<int:fid>")
@login_required
def edit_franchise(fid):
    """Update franchise"""
    b = request.json or {}
    name = (b.get("name") or "").strip()
    state = (b.get("state") or "").strip()

    if not name:
        return jsonify(error="Name required"), 400

    with db.cursor(commit=True) as cur:
        cur.execute("SELECT 1 FROM franchises WHERE LOWER(name)=LOWER(%s) AND id<>%s", (name, fid))
        if cur.fetchone():
            return jsonify(error="Already exists"), 409
        cur.execute("UPDATE franchises SET name=%s, state=%s WHERE id=%s", (name, state, fid))
    return jsonify(ok=True)


@app.delete("/api/franchises/<int:fid>")
@login_required
def del_franchise(fid):
    """Delete franchise"""
    with db.cursor(commit=True) as cur:
        cur.execute("SELECT COUNT(*) n FROM entries WHERE franchise_id=%s", (fid,))
        n = cur.fetchone()["n"]
        if n:
            return jsonify(error=f"In use by {n} entries"), 409
        cur.execute("DELETE FROM franchises WHERE id=%s", (fid,))
    return jsonify(ok=True)


# ============================================================================
# CATEGORIES
# ============================================================================

@app.post("/api/categories")
@login_required
def add_category():
    """Add category"""
    name = ((request.json or {}).get("name") or "").strip()
    if not name:
        return jsonify(error="Name required"), 400

    with db.cursor(commit=True) as cur:
        cur.execute("SELECT 1 FROM categories WHERE LOWER(name)=LOWER(%s)", (name,))
        if cur.fetchone():
            return jsonify(error="Already exists"), 409
        cur.execute("INSERT INTO categories(name) VALUES (%s) RETURNING id", (name,))
        return jsonify(id=cur.fetchone()["id"])


@app.put("/api/categories/<int:cid>")
@login_required
def edit_category(cid):
    """Update category"""
    name = ((request.json or {}).get("name") or "").strip()
    if not name:
        return jsonify(error="Name required"), 400

    with db.cursor(commit=True) as cur:
        cur.execute("SELECT 1 FROM categories WHERE LOWER(name)=LOWER(%s) AND id<>%s", (name, cid))
        if cur.fetchone():
            return jsonify(error="Already exists"), 409
        cur.execute("UPDATE categories SET name=%s WHERE id=%s", (name, cid))
    return jsonify(ok=True)


@app.delete("/api/categories/<int:cid>")
@login_required
def del_category(cid):
    """Delete category"""
    with db.cursor(commit=True) as cur:
        cur.execute("SELECT COUNT(*) n FROM categories")
        if cur.fetchone()["n"] <= 1:
            return jsonify(error="Keep at least one"), 409
        cur.execute("SELECT COUNT(*) n FROM entries WHERE category_id=%s", (cid,))
        n = cur.fetchone()["n"]
        if n:
            return jsonify(error=f"In use by {n} entries"), 409
        cur.execute("DELETE FROM categories WHERE id=%s", (cid,))
    return jsonify(ok=True)


# ============================================================================
# ENTRIES
# ============================================================================

def _filters(args):
    """Build WHERE clause"""
    w, params = [], []
    if args.get("from"):
        w.append("e.edate >= %s")
        params.append(args["from"])
    if args.get("to"):
        w.append("e.edate <= %s")
        params.append(args["to"])
    if args.get("franchise_id"):
        w.append("e.franchise_id = %s")
        params.append(int(args["franchise_id"]))
    if args.get("bill"):
        w.append("e.bill = %s")
        params.append(args["bill"])
    if args.get("q"):
        like = "%" + args["q"].lower() + "%"
        w.append(
            "(LOWER(f.name) LIKE %s OR LOWER(c.name) LIKE %s OR LOWER(e.descr) LIKE %s OR LOWER(e.invoice) LIKE %s)")
        params += [like, like, like, like]

    where = (" WHERE " + " AND ".join(w)) if w else ""
    return where, params


@app.get("/api/entries")
@login_required
def list_entries():
    """Get entries"""
    where, params = _filters(request.args)
    with db.cursor() as cur:
        cur.execute(ENTRY_SELECT + where + " ORDER BY e.edate DESC, e.id DESC", params)
        return jsonify(cur.fetchall())


@app.post("/api/entries")
@login_required
def add_entry():
    """Add entry"""
    b = request.json or {}

    if not b.get("franchise_id") or not b.get("category_id"):
        return jsonify(error="Franchise and category required"), 400
    if not (float(b.get("amount") or 0) > 0):
        return jsonify(error="Amount must be greater than zero"), 400

    with db.cursor(commit=True) as cur:
        cur.execute(
            "INSERT INTO entries(edate, franchise_id, category_id, descr, amount, invoice, bill, remarks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (b["date"], int(b["franchise_id"]), int(b["category_id"]), b.get("desc") or "",
             float(b["amount"]), b.get("invoice") or "", b.get("bill") or "Yes", b.get("remarks") or "")
        )
        return jsonify(id=cur.fetchone()["id"])


@app.put("/api/entries/<int:eid>")
@login_required
def edit_entry(eid):
    """Update entry"""
    b = request.json or {}

    if not (float(b.get("amount") or 0) > 0):
        return jsonify(error="Amount must be greater than zero"), 400

    with db.cursor(commit=True) as cur:
        cur.execute(
            "UPDATE entries SET edate=%s, franchise_id=%s, category_id=%s, descr=%s, amount=%s, invoice=%s, bill=%s, remarks=%s WHERE id=%s",
            (b["date"], int(b["franchise_id"]), int(b["category_id"]), b.get("desc") or "",
             float(b["amount"]), b.get("invoice") or "", b.get("bill") or "Yes", b.get("remarks") or "", eid)
        )
    return jsonify(ok=True)


@app.delete("/api/entries/<int:eid>")
@login_required
def del_entry(eid):
    """Delete entry"""
    with db.cursor(commit=True) as cur:
        cur.execute("DELETE FROM entries WHERE id=%s", (eid,))
    return jsonify(ok=True)


# ============================================================================
# BULK IMPORT
# ============================================================================

@app.post("/api/import")
@login_required
def bulk_import():
    """Bulk import"""
    b = request.json or {}
    rows = b.get("entries") or []

    if not rows:
        return jsonify(error="No rows"), 400

    if b.get("mode") == "replace" and ADMIN_PW and b.get("adminPassword") != ADMIN_PW:
        return jsonify(error="Admin password required"), 403

    with db.cursor(commit=True) as cur:
        if b.get("mode") == "replace":
            cur.execute("DELETE FROM entries")

        for f in (b.get("newFranchises") or []):
            name = (f.get("name") or "").strip()
            if not name:
                continue
            cur.execute(
                "INSERT INTO franchises(name, state) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING",
                (name, (f.get("state") or "").strip())
            )

        for c in (b.get("newCategories") or []):
            name = (c if isinstance(c, str) else c.get("name", "")).strip()
            if not name:
                continue
            cur.execute("INSERT INTO categories(name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (name,))

        cur.execute("SELECT id, name FROM franchises")
        fr = {r["name"].lower(): r["id"] for r in cur.fetchall()}

        cur.execute("SELECT id, name FROM categories")
        ct = {r["name"].lower(): r["id"] for r in cur.fetchall()}

        n = 0
        for e in rows:
            fid = fr.get((e.get("franchise") or "").lower())
            cid = ct.get((e.get("cat") or "").lower())

            if not fid or not cid or not (float(e.get("amount") or 0) > 0) or not e.get("date"):
                continue

            cur.execute(
                "INSERT INTO entries(edate, franchise_id, category_id, descr, amount, invoice, bill, remarks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (e["date"], fid, cid, e.get("desc") or "", float(e["amount"]),
                 e.get("invoice") or "", e.get("bill") or "Yes", e.get("remarks") or "")
            )
            n += 1

    return jsonify(inserted=n)


# ============================================================================
# EXPORT
# ============================================================================

@app.get("/api/export.csv")
@login_required
def export_csv():
    """Export CSV"""
    with db.cursor() as cur:
        cur.execute(ENTRY_SELECT + " ORDER BY e.edate, e.id")
        rows = cur.fetchall()

    buf = io.StringIO()
    wr = csv.writer(buf)
    wr.writerow(["Date", "Franchise", "State", "Category", "Description", "Amount", "Invoice", "Bill", "Remarks"])
    for r in rows:
        wr.writerow([r["date"], r["franchise"], r["state"], r["cat"], r["desc"], r["amount"], r["invoice"], r["bill"],
                     r["remarks"]])

    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=franchise_expenses.csv"}
    )


# ============================================================================
# FRONTEND
# ============================================================================

@app.get("/")
def index():
    """Serve HTML"""
    return send_from_directory(app.static_folder, "index.html")


# ============================================================================
# RUN
# ============================================================================

db.init_db()

if __name__ == "__main__":
    print("\n✅ Server starting...\n")
    app.run(host="0.0.0.0", port=3000, debug=False)