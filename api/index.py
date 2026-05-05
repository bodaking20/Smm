from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")
PRICE_PER_1000 = 9

def get_conn():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>طلب فولو فيسبوك</title>
<style>
body {
  margin:0;
  font-family:Tahoma, Arial;
  background:linear-gradient(135deg,#0052d4,#001b5e);
  color:white;
  padding:20px;
}
.card {
  max-width:520px;
  margin:auto;
  background:rgba(255,255,255,.13);
  padding:25px;
  border-radius:25px;
  text-align:center;
}
h1 { font-size:32px; }
.big { color:#ffcc00; font-size:45px; font-weight:bold; }
.price {
  background:white;
  color:#061b4a;
  padding:15px;
  border-radius:15px;
  font-size:24px;
  font-weight:bold;
  margin:15px 0;
}
input, textarea {
  width:100%;
  padding:14px;
  margin:8px 0;
  border:0;
  border-radius:12px;
  font-size:16px;
}
button {
  width:100%;
  padding:15px;
  border:0;
  border-radius:14px;
  background:#ffcc00;
  color:#061b4a;
  font-size:20px;
  font-weight:bold;
}
.total {
  background:rgba(255,255,255,.2);
  padding:12px;
  border-radius:12px;
  margin:10px 0;
  font-size:20px;
}
</style>
</head>
<body>
<div class="card">
  <h1>الـ <span class="big">1000 فولو</span><br>عليهم 1000 هدية</h1>
  <div class="price">السعر: 9ج لكل 1000</div>

  <form id="orderForm">
    <input id="name" placeholder="اسمك" required>
    <input id="phone" placeholder="رقم الموبايل" required>
    <input id="link" placeholder="لينك الصفحة أو الحساب" required>
    <input id="quantity" type="number" min="1" placeholder="عدد الألف - مثال: 2 = 2000 فولو" required oninput="calc()">
    <div class="total">السعر النهائي: <span id="total">0</span> جنيه</div>
    <textarea id="notes" placeholder="ملاحظات اختيارية"></textarea>
    <button type="submit">إرسال الطلب</button>
  </form>
</div>

<script>
function calc(){
  let q = document.getElementById("quantity").value || 0;
  document.getElementById("total").innerText = q * 9;
}

document.getElementById("orderForm").addEventListener("submit", async function(e){
  e.preventDefault();

  const data = {
    name: document.getElementById("name").value,
    phone: document.getElementById("phone").value,
    link: document.getElementById("link").value,
    quantity: document.getElementById("quantity").value,
    notes: document.getElementById("notes").value
  };

  const res = await fetch("/order", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(data)
  });

  if(res.ok){
    alert("تم إرسال الطلب بنجاح ✅");
    document.getElementById("orderForm").reset();
    document.getElementById("total").innerText = "0";
  } else {
    alert("حصل خطأ، حاول تاني");
  }
});
</script>
</body>
</html>
"""

@app.route("/order", methods=["POST"])
def order():
    data = request.json

    name = data.get("name")
    phone = data.get("phone")
    link = data.get("link")
    quantity = int(data.get("quantity"))
    notes = data.get("notes", "")
    total = quantity * PRICE_PER_1000

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
