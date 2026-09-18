from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv
from google import genai
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor
import re
import os
import urllib.parse
import random
from datetime import datetime, timedelta
from flask_mail import Mail, Message

load_dotenv()

app = Flask(__name__)

# Secret key for login sessions
app.secret_key = "tyre_store_secret_key"

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_EMAIL")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)

# WhatsApp number
# Replace this later with the actual business WhatsApp number
WHATSAPP_NUMBER = "91XXXXXXXXXX"


# =========================================================
# GEMINI CHATBOT SETUP
# =========================================================

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conn

def init_db():

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_verified INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS otp_verifications (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            otp TEXT NOT NULL,
            expires_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tyres (
            id SERIAL PRIMARY KEY,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            size TEXT NOT NULL,
            position TEXT NOT NULL,
            availability TEXT NOT NULL,
            price REAL NOT NULL,
            image TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS favourites (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            tyre_id INTEGER
        )
    """)

    cur.execute("SELECT COUNT(*) AS count FROM tyres")
    count = cur.fetchone()["count"]

    if count == 0:

        sample_tyres = [
            (
                "MRF",
                "ZVTS",
                "175/65 R15",
                "Front / Rear",
                "Available",
                4500,
                "tyre1.jpg"
            ),
            (
                "CEAT",
                "Milaze",
                "185/65 R15",
                "Front / Rear",
                "Available",
                4800,
                "tyre2.jpg"
            ),
            (
                "Apollo",
                "Amazer 4G",
                "195/65 R15",
                "Front / Rear",
                "Available",
                5200,
                "tyre3.jpg"
            ),
            (
                "Bridgestone",
                "B290",
                "205/55 R16",
                "Front / Rear",
                "Out of Stock",
                6500,
                "tyre4.jpg"
            )
        ]

        cur.executemany("""
            INSERT INTO tyres
            (brand, model, size, position, availability, price, image)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, sample_tyres)

    conn.commit()
    cur.close()
    conn.close()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT * FROM tyres
        ORDER BY id DESC
        LIMIT 4
    """)

    featured_tyres = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "home.html",
        featured_tyres=featured_tyres
    )

# =========================================================
# SERVICES
# =========================================================

@app.route("/services")
def services():
    return render_template("services.html")


# =========================================================
# FAVOURITES PAGE
# =========================================================

@app.route("/favourites")
def favourites():

    if not session.get("user_id"):
        return render_template("favourites.html")

    user_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT tyres.*
        FROM tyres
        INNER JOIN favourites
        ON tyres.id = favourites.tyre_id
        WHERE favourites.user_id=%s
        ORDER BY tyres.id DESC
    """, (user_id,))

    favourite_tyres = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "favourites.html",
        tyres=favourite_tyres
    )

# =========================================================
# CATALOGUE
# =========================================================

@app.route("/catalogue")
def catalogue():

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT * FROM tyres ORDER BY id DESC"
    )

    tyres = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "catalogue.html",
        tyres=tyres
    )

# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"].lower()
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        existing_user = None

        cur.execute(
            "SELECT id FROM users WHERE email=%s",
            (email,)
        )
        existing_user = cur.fetchone()

        if existing_user:
            cur.close()
            conn.close()

            return render_template(
                "register.html",
                error="Email already registered."
            )

        hashed_password = generate_password_hash(password)

        otp = str(random.randint(100000, 999999))
        expires_at = datetime.now() + timedelta(minutes=10)

        cur.execute(
            "DELETE FROM otp_verifications WHERE email=%s",
            (email,)
        )

        cur.execute("""
            INSERT INTO otp_verifications
            (name, email, password, otp, expires_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            name,
            email,
            hashed_password,
            otp,
            expires_at.isoformat()
        ))

        conn.commit()

        cur.close()
        conn.close()

        msg = Message(
            "Kedar Tyres - Email Verification OTP",
            sender=os.getenv("MAIL_EMAIL"),
            recipients=[email]
        )

        msg.body = f"""
Hello {name},

Your Kedar Tyres verification OTP is:

{otp}

This OTP is valid for 10 minutes.

If you did not request this, please ignore this email.
"""

        mail.send(msg)

        session["verification_email"] = email

        return redirect(url_for("verify_otp"))

    return render_template("register.html")

# =========================================================
# VERIFY OTP
# =========================================================

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():

    email = session.get("verification_email")

    if not email:
        return redirect(url_for("register"))

    if request.method == "POST":

        entered_otp = request.form["otp"]

        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT *
            FROM otp_verifications
            WHERE email=%s
            ORDER BY id DESC
            LIMIT 1
        """, (email,))

        verification = cur.fetchone()

        if not verification:
            cur.close()
            conn.close()

            return render_template(
                "verify_otp.html",
                error="OTP not found. Please register again."
            )

        expires_at = datetime.fromisoformat(
            verification["expires_at"]
        )

        if datetime.now() > expires_at:

            cur.close()
            conn.close()

            return render_template(
                "verify_otp.html",
                error="OTP has expired. Please register again."
            )

        if entered_otp != verification["otp"]:

            cur.close()
            conn.close()

            return render_template(
                "verify_otp.html",
                error="Invalid OTP."
            )

        cur.execute("""
            INSERT INTO users
            (name, email, password, is_verified)
            VALUES (%s, %s, %s, %s)
        """, (
            verification["name"],
            verification["email"],
            verification["password"],
            1
        ))

        cur.execute(
            "DELETE FROM otp_verifications WHERE email=%s",
            (email,)
        )

        conn.commit()

        cur.close()
        conn.close()

        session.pop("verification_email", None)

        return redirect(url_for("login"))

    return render_template("verify_otp.html")

# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].lower()
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cur.fetchone()

        cur.close()
        conn.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            return redirect(url_for("catalogue"))

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template("login.html")

# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        # Demo admin credentials
        if username == "admin" and password == "admin123":

            session["admin"] = True

            return redirect(url_for("admin_dashboard"))

        return render_template(
            "admin_login.html",
            error="Invalid admin credentials."
        )

    return render_template("admin_login.html")


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
def admin_dashboard():

    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT * FROM tyres ORDER BY id DESC"
    )

    tyres = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        tyres=tyres
    )

# =========================================================
# ADD TYRE
# =========================================================

@app.route("/admin/add-tyre", methods=["POST"])
def add_tyre():

    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    brand = request.form["brand"]
    model = request.form["model"]
    size = request.form["size"]
    position = request.form["position"]
    availability = request.form["availability"]
    price = request.form["price"]
    image = request.form["image"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO tyres
        (brand, model, size, position, availability, price, image)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        brand,
        model,
        size,
        position,
        availability,
        price,
        image
    ))

    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for("admin_dashboard"))


# =========================================================
# DELETE TYRE
# =========================================================

@app.route("/admin/delete/<int:tyre_id>")
def delete_tyre(tyre_id):

    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM tyres WHERE id=%s",
        (tyre_id,)
    )

    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for("admin_dashboard"))


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin", None)

    return redirect(url_for("home"))


# =========================================================
# WHATSAPP
# =========================================================

@app.route("/whatsapp/<int:tyre_id>")
def whatsapp(tyre_id):

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT * FROM tyres WHERE id=%s",
        (tyre_id,)
    )

    tyre = cur.fetchone()

    cur.close()
    conn.close()

    if not tyre:
        return redirect(url_for("catalogue"))

    message = (
        f"Hello, I am interested in {tyre['brand']} "
        f"{tyre['model']} tyre, size {tyre['size']}."
    )

    whatsapp_url = (
        "https://wa.me/"
        + WHATSAPP_NUMBER
        + "%stext="
        + urllib.parse.quote(message)
    )

    return redirect(whatsapp_url)

# =========================================================
# FAVOURITE / UNFAVOURITE
# =========================================================

@app.route("/favourite/<int:tyre_id>")
def favourite(tyre_id):

    if not session.get("user_id"):
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT * FROM favourites
        WHERE user_id=%s AND tyre_id=%s
    """, (
        user_id,
        tyre_id
    ))

    existing = cur.fetchone()

    if existing:

        cur.execute("""
            DELETE FROM favourites
            WHERE user_id=%s AND tyre_id=%s
        """, (
            user_id,
            tyre_id
        ))

    else:

        cur.execute("""
            INSERT INTO favourites
            (user_id, tyre_id)
            VALUES (%s, %s)
        """, (
            user_id,
            tyre_id
        ))

    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for("catalogue"))

# ================================
# SEARCH TYRE BY SIZE
# ================================

@app.route("/api/search-tyre")
def search_tyre():

    query = request.args.get("size", "").strip()

    if not query:
        return jsonify([])

    # Keep only numbers.
    normalized_query = re.sub(r"[^0-9]", "", query)

    if not normalized_query:
        return jsonify([])

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            id,
            brand,
            model,
            size,
            position,
            availability,
            price,
            image
        FROM tyres
        ORDER BY id DESC
    """)

    tyres = cur.fetchall()

    cur.close()
    conn.close()

    results = []

    for tyre in tyres:

        normalized_db_size = re.sub(
            r"[^0-9]",
            "",
            tyre["size"]
        )

        if normalized_db_size == normalized_query:

            results.append({
                "id": tyre["id"],
                "brand": tyre["brand"],
                "model": tyre["model"],
                "size": tyre["size"],
                "position": tyre["position"],
                "availability": tyre["availability"],
                "price": tyre["price"],
                "image": tyre["image"]
            })

    return jsonify(results)

# chatbot

@app.route("/api/chat", methods=["POST"])
def chat():

    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({
            "reply": "Sorry, I can't help you with that request :)"
        })

    greetings = [
        "hi",
        "hii",
        "hiii",
        "hello",
        "hey",
        "heyy",
        "good morning",
        "good afternoon",
        "good evening"
    ]

    if user_message.lower() in greetings:
        return jsonify({
            "reply": "Hello! 👋 How can I help you with your tyres today?"
        })

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT brand, model, size, position, availability, price
        FROM tyres
        ORDER BY brand, model
    """)

    tyres = cur.fetchall()

    cur.close()
    conn.close()

    # Create catalogue information for Gemini

    catalogue_info = []

    for tyre in tyres:

        catalogue_info.append(
            f"Brand: {tyre['brand']}, "
            f"Model: {tyre['model']}, "
            f"Size: {tyre['size']}, "
            f"Position: {tyre['position']}, "
            f"Availability: {tyre['availability']}, "
            f"Price: ₹{tyre['price']}"
        )


    if catalogue_info:

        catalogue_text = "\n".join(catalogue_info)

    else:

        catalogue_text = "The XYZ Tyres catalogue is currently empty."


    # =========================================
    # AI INSTRUCTIONS
    # =========================================

    system_instruction = f"""
You are the helpful AI assistant for XYZ Tyres.

Your job is to assist visitors with questions related to:

- tyres
- tyre brands
- tyre models
- tyre sizes
- vehicles
- tyre compatibility
- tyre maintenance
- tyre care
- tyre pressure
- tyre services
- tyre fitting
- wheel alignment
- wheel balancing
- puncture repair
- tyre rotation
- tyre inspection
- products available in the XYZ Tyres catalogue
- information about the XYZ Tyres website

IMPORTANT:

You have access to the CURRENT XYZ TYRES CATALOGUE below.

Use this catalogue information when answering questions about
XYZ Tyres products, brands, models, sizes, availability and prices.

CURRENT XYZ TYRES CATALOGUE:

{catalogue_text}


CATALOGUE RULES:

1. If the user asks which tyre brands XYZ Tyres provides,
   list the unique brands present in the catalogue.

2. If the user asks about a specific brand, only give information
   that is present in the catalogue.

3. If the user asks about a tyre model, size, availability or price,
   use the catalogue information above.

4. Do not invent products, brands, prices, sizes or availability.

5. If the requested product information is not present in the
   catalogue, say:

   Sorry, I can't help you with that request :)

6. For general tyre questions, you may provide general tyre knowledge.

7. For questions about XYZ Tyres business information that is not
   provided in the catalogue, do not invent information.

8. For questions completely unrelated to tyres, vehicles, tyre
   services, tyre products or the XYZ Tyres website, reply exactly:

   Sorry, I can't help you with that request :)

Keep answers clear, friendly and reasonably short.
"""


    # =========================================
    # GEMINI
    # =========================================

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=(
                system_instruction
                + "\n\nUser question:\n"
                + user_message
            )
        )

        return jsonify({
            "reply": response.text
        })

    except Exception as e:

        print("Gemini error:", e)

        return jsonify({
            "reply": "Sorry, I can't help you with that request :)"
        })


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    init_db()

    app.run(debug=True)

