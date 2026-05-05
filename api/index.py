from flask import Flask, request, jsonify, redirect, session
import psycopg2
import os
from functools import wraps

app = Flask(__name__)
application = app
handler = app

app.secret_key = os.environ.get("SECRET_KEY", "boda_secret_1512005_!@#_secure")

DATABASE_URL = os.environ.get("DATABASE_URL")
PRICE_PER_1000 = 9

ADMIN_USER = "boda"
ADMIN_PASSWORD = "Bb#1512005"


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("admin_logged_in") != True:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper


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
*{box-sizing:border-box}
body{
  margin:0;
  font-family:Tahoma,Arial;
  background:radial-gradient(circle at top,#1267ff,#061b4a 55%,#020b22);
  color:white;
  padding:18px;
}
.card{
  max-width:560px;
  margin:auto;
  background:rgba(255,255,255,.14);
  padding:24px;
  border-radius:28px;
  text-align:center;
  border:1px solid rgba(255,255,255,.25);
  box-shadow:0 20px 60px rgba(0,0,0,.35);
}
.badge{
  display:inline-block;
  background:#ffcc00;
  color:#061b4a;
  padding:9px 18px;
  border-radius:999px;
  font-weight:bold;
  margin-bottom:14px;
}
h1{font-size:32px;margin:10px 0}
.big{color:#ffcc00;font-size:48px;font-weight:bold}
.subtitle{font-size:17px;opacity:.95;line-height:1.8}
.price{
  background:white;
  color:#061b4a;
  padding:15px;
  border-radius:18px;
  font-size:24px;
  font-weight:bold;
  margin:15px 0;
}
.price span{color:#e51b23;font-size:34px}
.features{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:10px;
  margin:15px 0;
}
.feature{
  background:rgba(255,255,255,.18);
  border:1px solid rgba(255,255,255,.22);
  border-radius:18px;
  padding:14px 10px;
}
.feature strong{
  display:block;
  color:#ffcc00;
  font-size:20px;
  margin-top:5px;
}
input,textarea{
  width:100%;
  padding:15px;
  margin:8px 0;
  border:0;
  border-radius:14px;
  font-size:16px;
  outline:none;
}
textarea{min-height:85px;resize:vertical}
button{
  width:100%;
  padding:16px;
  border:0;
  border-radius:16px;
  background:#ffcc00;
  color:#061b4a;
  font-size:20px;
  font-weight:bold;
  cursor:pointer;
}
.total{
  background:rgba(255,255,255,.22);
  padding:13px;
  border-radius:14px;
  margin:10px 0;
  font-size:20px;
  font-weight:bold;
}
.note{
  font-size:13px;
  opacity:.85;
  margin-top:12px;
}
@media(max-width:430px){
  .features{grid-template-columns:1fr}
  h1{font-size:28px}
  .big{font-size:42px}
}
</style>
</head>
<body>
<div class="card">
  <div class="badge">عرض خاص لفترة محدودة</div>

  <h1>الـ <span class="big">1000 فولو</span><br>عليهم 1000 هدية</h1>
  <p class="subtitle">زوّد جمهورك بسرعة وبسعر بسيط مع ضمان كامل على الخدمة.</p>

  <div class="price">السعر: <span>9ج</span> لكل 1000</div>

  <div class="features">
    <div class="feature">فترة ضمان<strong>شهرين</strong></div>
    <div class="feature">سرعة التنفيذ<strong>1,000,000 في اليوم</strong></div>
  </div>

  <form id="orderForm">
    <input id="name" placeholder="اسمك" required>
    <input id="phone" placeholder="رقم الموبايل" required>
    <input id="link" placeholder="لينك الصفحة أو الحساب" required>
    <input id="quantity" type="number" min="1" placeholder="عدد الألف - مثال: 2 = 2000 فولو" required oninput="calc()">
    <div class="total">السعر النهائي: <span id="total">0</span> جنيه</div>
    <textarea id="notes" placeholder="ملاحظات اختيارية"></textarea>
    <button type="submit">إرسال الطلب</button>
  </form>

  <div class="note">بعد إرسال الطلب سيتم تسجيله في لوحة الأدمن مباشرة.</div>
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


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USER and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect("/admin")
        else:
            error = "اليوزر أو الباسورد غلط"

    return f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>تسجيل دخول الأدمن</title>
<style>
body {{
  margin:0;
  font-family:Tahoma, Arial;
  background:linear-gradient(135deg,#001b5e,#0052d4);
  min-height:100vh;
  display:flex;
  align-items:center;
  justify-content:center;
  padding:20px;
}}
.box {{
  width:100%;
  max-width:420px;
  background:white;
  padding:25px;
  border-radius:22px;
  text-align:center;
  box-shadow:0 20px 50px rgba(0,0,0,.3);
}}
h1 {{ color:#061b4a; }}
input {{
  width:100%;
  padding:14px;
  margin:10px 0;
  border:1px solid #ddd;
  border-radius:12px;
  font-size:16px;
  box-sizing:border-box;
}}
button {{
  width:100%;
  padding:15px;
  border:0;
  border-radius:14px;
  background:#ffcc00;
  color:#061b4a;
  font-size:20px;
  font-weight:bold;
}}
.error {{ color:red; margin:10px 0; }}
</style>
</head>
<body>
<div class="box">
  <h1>تسجيل دخول الأدمن</h1>
  <form method="POST">
    <input name="username" placeholder="Username" required>
    <input name="password" type="password" placeholder="Password" required>
    <div class="error">{error}</div>
    <button type="submit">دخول</button>
  </form>
</div>
</body>
</html>
"""


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/admin")
@login_required
def admin():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, phone, link, quantity, total_price, created_at
        FROM orders
        ORDER BY id DESC
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    table_rows = ""

    for row in rows:
        table_rows += f"""
        <tr>
            <td>{row[0]}</td>
            <td>{row[1]}</td>
            <td><a href="tel:{row[2]}">{row[2]}</a></td>
            <td><a href="{row[3]}" target="_blank">فتح اللينك</a></td>
            <td>{row[4] * 1000} فولو</td>
            <td>{row[5]} ج</td>
            <td>{row[6]}</td>
        </tr>
        """

    return f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>لوحة الأدمن</title>
<style>
body {{
  margin:0;
  font-family:Tahoma, Arial;
  background:#081a3d;
  color:white;
  padding:15px;
}}
.header {{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:20px;
}}
h1 {{ margin:0; }}
.logout {{
  background:#ff4444;
  color:white;
  padding:10px 14px;
  border-radius:10px;
  text-decoration:none;
  font-weight:bold;
}}
.table-wrap {{
  overflow-x:auto;
  background:white;
  border-radius:16px;
}}
table {{
  width:100%;
  border-collapse:collapse;
  min-width:800px;
  color:#111;
}}
th {{
  background:#ffcc00;
  color:#061b4a;
  padding:12px;
}}
td {{
  padding:12px;
  text-align:center;
  border-bottom:1px solid #ddd;
}}
tr:hover {{ background:#f5f5f5; }}
a {{ color:#0052d4; font-weight:bold; }}
.empty {{
  text-align:center;
  background:white;
  color:#061b4a;
  padding:30px;
  border-radius:16px;
  font-size:20px;
}}
</style>
</head>
<body>
<div class="header">
  <h1>📦 طلبات العملاء</h1>
  <a class="logout" href="/logout">خروج</a>
</div>

{"<div class='empty'>لا توجد طلبات حتى الآن</div>" if not rows else f'''
<div class="table-wrap">
<table>
  <tr>
    <th>ID</th>
    <th>الاسم</th>
    <th>الموبايل</th>
    <th>اللينك</th>
    <th>الكمية</th>
    <th>السعر</th>
    <th>التاريخ</th>
  </tr>
  {table_rows}
</table>
</div>
'''}
</body>
</html>
"""  border-radius:14px;
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


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USER and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect("/admin")
        else:
            error = "اليوزر أو الباسورد غلط"

    return f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>تسجيل دخول الأدمن</title>
<style>
body {{
  margin:0;
  font-family:Tahoma, Arial;
  background:linear-gradient(135deg,#001b5e,#0052d4);
  min-height:100vh;
  display:flex;
  align-items:center;
  justify-content:center;
  padding:20px;
}}
.box {{
  width:100%;
  max-width:420px;
  background:white;
  padding:25px;
  border-radius:22px;
  text-align:center;
  box-shadow:0 20px 50px rgba(0,0,0,.3);
}}
h1 {{ color:#061b4a; }}
input {{
  width:100%;
  padding:14px;
  margin:10px 0;
  border:1px solid #ddd;
  border-radius:12px;
  font-size:16px;
  box-sizing:border-box;
}}
button {{
  width:100%;
  padding:15px;
  border:0;
  border-radius:14px;
  background:#ffcc00;
  color:#061b4a;
  font-size:20px;
  font-weight:bold;
}}
.error {{ color:red; margin:10px 0; }}
</style>
</head>
<body>
<div class="box">
  <h1>تسجيل دخول الأدمن</h1>
  <form method="POST">
    <input name="username" placeholder="Username" required>
    <input name="password" type="password" placeholder="Password" required>
    <div class="error">{error}</div>
    <button type="submit">دخول</button>
  </form>
</div>
</body>
</html>
"""


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/admin")
@login_required
def admin():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, phone, link, quantity, total_price, created_at
        FROM orders
        ORDER BY id DESC
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    table_rows = ""

    for row in rows:
        table_rows += f"""
        <tr>
            <td>{row[0]}</td>
            <td>{row[1]}</td>
            <td><a href="tel:{row[2]}">{row[2]}</a></td>
            <td><a href="{row[3]}" target="_blank">فتح اللينك</a></td>
            <td>{row[4] * 1000} فولو</td>
            <td>{row[5]} ج</td>
            <td>{row[6]}</td>
        </tr>
        """

    return f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>لوحة الأدمن</title>
<style>
body {{
  margin:0;
  font-family:Tahoma, Arial;
  background:#081a3d;
  color:white;
  padding:15px;
}}
.header {{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:20px;
}}
h1 {{ margin:0; }}
.logout {{
  background:#ff4444;
  color:white;
  padding:10px 14px;
  border-radius:10px;
  text-decoration:none;
  font-weight:bold;
}}
.table-wrap {{
  overflow-x:auto;
  background:white;
  border-radius:16px;
}}
table {{
  width:100%;
  border-collapse:collapse;
  min-width:800px;
  color:#111;
}}
th {{
  background:#ffcc00;
  color:#061b4a;
  padding:12px;
}}
td {{
  padding:12px;
  text-align:center;
  border-bottom:1px solid #ddd;
}}
tr:hover {{ background:#f5f5f5; }}
a {{ color:#0052d4; font-weight:bold; }}
.empty {{
  text-align:center;
  background:white;
  color:#061b4a;
  padding:30px;
  border-radius:16px;
  font-size:20px;
}}
</style>
</head>
<body>
<div class="header">
  <h1>📦 طلبات العملاء</h1>
  <a class="logout" href="/logout">خروج</a>
</div>

{"<div class='empty'>لا توجد طلبات حتى الآن</div>" if not rows else f'''
<div class="table-wrap">
<table>
  <tr>
    <th>ID</th>
    <th>الاسم</th>
    <th>الموبايل</th>
    <th>اللينك</th>
    <th>الكمية</th>
    <th>السعر</th>
    <th>التاريخ</th>
  </tr>
  {table_rows}
</table>
</div>
'''}
</body>
</html>
"""
