from flask import Flask, render_template, request, redirect, send_file
import sqlite3
from datetime import datetime
import os
import pandas as pd

app = Flask(__name__)
DB_NAME = "orders.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            drink_type TEXT,
            tokens INTEGER,
            redeemed INTEGER,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        drink = request.form["drink"]
        tokens = int(request.form["tokens"])
        redeemed = 1 if "redeemed" in request.form else 0
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO orders (customer_name, drink_type, tokens, redeemed, date) VALUES (?, ?, ?, ?, ?)",
                  (name, drink, tokens, redeemed, date))
        conn.commit()
        conn.close()
        return redirect("/")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY date DESC")
    orders = c.fetchall()
    conn.close()
    return render_template("index.html", orders=orders)

@app.route("/export")
def export():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM orders", conn)
    conn.close()

    if df.empty:
        return "No data to export"

    df["Redeemed?"] = df["redeemed"].apply(lambda x: "Yes" if x else "No")
    df = df[["customer_name", "date", "drink_type", "tokens", "Redeemed?"]]
    df.columns = ["Customer Name", "Date", "Drink Type", "Tokens Earned", "Redeemed?"]

    output_file = "orders.xlsx"
    df.to_excel(output_file, index=False)
    return send_file(output_file, as_attachment=True)

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)