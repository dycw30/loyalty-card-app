from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import csv
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            customer_name TEXT,
            drink_type TEXT,
            tokens INTEGER,
            redeemed BOOLEAN DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_order', methods=['POST'])
def submit_order():
    name = request.form['name']
    drink = request.form['drink']
    tokens = int(request.form['tokens'])

    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('INSERT INTO orders (customer_name, drink_type, tokens) VALUES (?, ?, ?)',
              (name, drink, tokens))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/export')
def export():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT * FROM orders')
    rows = c.fetchall()
    conn.close()

    filename = 'orders_export.csv'
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Customer', 'Drink', 'Tokens', 'Redeemed', 'Timestamp'])
        writer.writerows(rows)

    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)