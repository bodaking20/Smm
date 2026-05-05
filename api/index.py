from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def home():
    return "API is running"

@app.route("/order", methods=["POST"])
def order():
    data = request.json

    name = data.get("name")
    phone = data.get("phone")
    link = data.get("link")
    quantity = int(data.get("quantity"))
    total = quantity * 9

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO orders (name, phone, link, quantity, total_price)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, phone, link, quantity, total))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "success"})

@app.route("/admin")
def admin():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id, name, phone, link, quantity, total_price, created_at FROM orders ORDER BY id DESC")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(rows)
