from flask import request, redirect, render_template, url_for
from flask_login import login_user, logout_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

def get_user_by_username(username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def register_user(username, password):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, generate_password_hash(password))
    )
    conn.commit()
    conn.close()
