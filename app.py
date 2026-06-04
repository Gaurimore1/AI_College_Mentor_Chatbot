from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from db import init_db, get_db
from auth import User, get_user_by_username, register_user
from rag_engine import get_rag_response

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

init_db()

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1])
    return None

@app.route("/", methods=["GET"])
@login_required
def home():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT message, response
        FROM chats
        WHERE user_id = ?
        ORDER BY timestamp ASC
    """, (current_user.id,))

    history = cursor.fetchall()
    conn.close()

    return render_template(
        "index.html",
        username=current_user.username,
        history=history
    )

@app.route("/chat", methods=["POST"])
@login_required
def chat():
    user_message = request.json["message"]
    print("USER QUESTION:", user_message)

    try:
        reply = get_rag_response(user_message)
        print("MENTOR REPLY:", reply)

    except Exception as e:
        print("ERROR FROM get_rag_response:", e)
        reply = "Error generating response."

    # Save chat history
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chats (user_id, message, response) VALUES (?, ?, ?)",
        (current_user.id, user_message, reply)
    )
    conn.commit()
    conn.close()

    return jsonify({"reply": reply})


@app.route("/history")
@login_required
def history():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT message, response, timestamp
        FROM chats
        WHERE user_id = ?
        ORDER BY timestamp DESC
    """, (current_user.id,))

    rows = cursor.fetchall()
    conn.close()

    return jsonify(rows)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = get_user_by_username(username)
        if user and check_password_hash(user[2], password):
            login_user(User(user[0], user[1]))
            return redirect(url_for("home"))

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        register_user(request.form["username"], request.form["password"])
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
