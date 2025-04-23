from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
import sqlite3
import dns.resolver
import dns.update
import dns.query
import dns.tsigkeyring
from dns.rdataclass import IN
from dns.rdatatype import A, CNAME, MX, TXT
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # For flash messages

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('dns_records.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS records
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  domain TEXT NOT NULL,
                  name TEXT NOT NULL,
                  type TEXT NOT NULL,
                  value TEXT NOT NULL,
                  ttl INTEGER DEFAULT 300)''')
    conn.commit()
    conn.close()

# Helper to connect to SQLite
def get_db():
    conn = sqlite3.connect('dns_records.db')
    conn.row_factory = sqlite3.Row
    return conn

# Simulated DNS server configuration
DNS_SERVER = "127.0.0.1"
DOMAIN = "aman@cloud"
KEYRING = None

# Simulate DNS update
def update_dns_record(domain, name, rtype, value, ttl, action="UPSERT"):
    try:
        print(f"Simulated DNS {action}: {name}.{domain} {rtype} {value} TTL {ttl}")
        return True
    except Exception as e:
        print(f"DNS update error: {e}")
        return False

# Web Routes
@app.route('/')
def index():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM records WHERE domain = ?", (DOMAIN,))
    records = [dict(row) for row in c.fetchall()]
    conn.close()
    return render_template('index.html', records=records, domain=DOMAIN)

@app.route('/add', methods=['GET', 'POST'])
def add_record():
    if request.method == 'POST':
        domain = request.form.get('domain', DOMAIN)
        name = request.form.get('name')
        rtype = request.form.get('type')
        value = request.form.get('value')
        ttl = request.form.get('ttl', 300, type=int)

        if not all([name, rtype, value]) or rtype not in ['A', 'CNAME', 'MX', 'TXT']:
            flash("Invalid input. Please check all fields.", "danger")
            return redirect(url_for('add_record'))

        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO records (domain, name, type, value, ttl) VALUES (?, ?, ?, ?, ?)",
                  (domain, name, rtype, value, ttl))
        conn.commit()

        if update_dns_record(domain, name, rtype, value, ttl):
            flash("Record created successfully!", "success")
            conn.close()
            return redirect(url_for('index'))
        else:
            flash("Failed to update DNS.", "danger")
            conn.close()
            return redirect(url_for('add_record'))

    return render_template('add.html',DOMAIN=DOMAIN)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_record(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM records WHERE id = ?", (id,))
    record = c.fetchone()
    if not record:
        flash("Record not found.", "danger")
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name')
        rtype = request.form.get('type')
        value = request.form.get('value')
        ttl = request.form.get('ttl', 300, type=int)

        if not all([name, rtype, value]) or rtype not in ['A', 'CNAME', 'MX', 'TXT']:
            flash("Invalid input. Please check all fields.", "danger")
            conn.close()
            return redirect(url_for('edit_record', id=id))

        c.execute("UPDATE records SET name = ?, type = ?, value = ?, ttl = ? WHERE id = ?",
                  (name, rtype, value, ttl, id))
        conn.commit()

        if update_dns_record(record['domain'], name, rtype, value, ttl):
            flash("Record updated successfully!", "success")
            conn.close()
            return redirect(url_for('index'))
        else:
            flash("Failed to update DNS.", "danger")
            conn.close()
            return redirect(url_for('edit_record', id=id))

    conn.close()
    return render_template('edit.html', record=record)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_record(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM records WHERE id = ?", (id,))
    record = c.fetchone()
    if not record:
        flash("Record not found.", "danger")
        conn.close()
        return redirect(url_for('index'))

    c.execute("DELETE FROM records WHERE id = ?", (id,))
    conn.commit()

    if update_dns_record(record['domain'], record['name'], record['type'], "", 300, action="DELETE"):
        flash("Record deleted successfully!", "success")
    else:
        flash("Failed to delete DNS record.", "danger")
    conn.close()
    return redirect(url_for('index'))

# API Routes (for future extensibility)
@app.route('/api/records', methods=['POST'])
def api_create_record():
    data = request.get_json()
    domain = data.get('domain', DOMAIN)
    name = data.get('name')
    rtype = data.get('type')
    value = data.get('value')
    ttl = data.get('ttl', 300)

    if not all([name, rtype, value]) or rtype not in ['A', 'CNAME', 'MX', 'TXT']:
        return jsonify({"error": "Invalid input"}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO records (domain, name, type, value, ttl) VALUES (?, ?, ?, ?, ?)",
              (domain, name, rtype, value, ttl))
    conn.commit()

    if update_dns_record(domain, name, rtype, value, ttl):
        conn.close()
        return jsonify({"message": "Record created", "record": data}), 201
    else:
        conn.close()
        return jsonify({"error": "DNS update failed"}), 500

@app.route('/api/records', methods=['GET'])
def api_list_records():
    domain = request.args.get('domain', DOMAIN)
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM records WHERE domain = ?", (domain,))
    records = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(records)

@app.route('/api/records/<int:id>', methods=['PUT'])
def api_update_record(id):
    data = request.get_json()
    name = data.get('name')
    rtype = data.get('type')
    value = data.get('value')
    ttl = data.get('ttl', 300)

    if not all([name, rtype, value]) or rtype not in ['A', 'CNAME', 'MX', 'TXT']:
        return jsonify({"error": "Invalid input"}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM records WHERE id = ?", (id,))
    record = c.fetchone()
    if not record:
        conn.close()
        return jsonify({"error": "Record not found"}), 404

    c.execute("UPDATE records SET name = ?, type = ?, value = ?, ttl = ? WHERE id = ?",
              (name, rtype, value, ttl, id))
    conn.commit()

    if update_dns_record(record['domain'], name, rtype, value, ttl):
        conn.close()
        return jsonify({"message": "Record updated", "record": data})
    else:
        conn.close()
        return jsonify({"error": "DNS update failed"}), 500

@app.route('/api/records/<int:id>', methods=['DELETE'])
def api_delete_record(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM records WHERE id = ?", (id,))
    record = c.fetchone()
    if not record:
        conn.close()
        return jsonify({"error": "Record not found"}), 404

    c.execute("DELETE FROM records WHERE id = ?", (id,))
    conn.commit()

    if update_dns_record(record['domain'], record['name'], record['type'], "", 300, action="DELETE"):
        conn.close()
        return jsonify({"message": "Record deleted"})
    else:
        conn.close()
        return jsonify({"error": "DNS delete failed"}), 500

if __name__ == '__main__':
    if not os.path.exists('dns_records.db'):
        init_db()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')
