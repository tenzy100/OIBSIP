#!/usr/bin/env python3
"""
Web-based Chat Application
Oasis Infobyte Summer Internship Program

A modern web-based chat application using Flask and SocketIO
Features: Real-time messaging, multiple rooms, user authentication, emoji support
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3
import hashlib
import secrets
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
socketio = SocketIO(app, cors_allowed_origins="*")

# Database setup
def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('chat_app.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS chat_rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            message_type TEXT DEFAULT 'text',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES chat_rooms (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create default general room
    try:
        conn.execute("INSERT OR IGNORE INTO chat_rooms (name, description) VALUES (?, ?)",
                    ("general", "General discussion room"))
        conn.commit()
    except:
        pass

    conn.close()

init_db()

# Password hashing functions
def hash_password(password, salt=None):
    """Hash password with salt"""
    if salt is None:
        salt = secrets.token_hex(16)

    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return pwd_hash.hex(), salt

def verify_password(password, stored_hash, salt):
    """Verify password against stored hash"""
    pwd_hash, _ = hash_password(password, salt)
    return pwd_hash == stored_hash

# Emoji mappings
EMOJI_MAP = {
    ":smile:": "😊", ":laugh:": "😂", ":wink:": "😉", ":heart:": "❤️",
    ":thumbs_up:": "👍", ":thumbs_down:": "👎", ":clap:": "👏", ":pray:": "🙏",
    ":fire:": "🔥", ":100:": "💯", ":party:": "🎉", ":rocket:": "🚀",
    ":sun:": "☀️", ":moon:": "🌙", ":star:": "⭐", ":rainbow:": "🌈",
    ":pizza:": "🍕", ":coffee:": "☕", ":beer:": "🍺", ":cake:": "🎂"
}

@app.route('/')
def index():
    """Main page - redirect to login if not authenticated"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            return render_template('login.html', error="Please enter both username and password")

        conn = sqlite3.connect('chat_app.db')
        cursor = conn.execute("SELECT id, password_hash, salt FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and verify_password(password, user[1], user[2]):
            session['user_id'] = user[0]
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        if not username or not password or not confirm:
            return render_template('register.html', error="Please fill in all fields")

        if password != confirm:
            return render_template('register.html', error="Passwords do not match")

        if len(password) < 6:
            return render_template('register.html', error="Password must be at least 6 characters")

        # Hash password
        password_hash, salt = hash_password(password)

        try:
            conn = sqlite3.connect('chat_app.db')
            conn.execute(
                "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                (username, password_hash, salt)
            )
            conn.commit()
            conn.close()

            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error="Username already exists")

    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/rooms')
def get_rooms():
    """API endpoint to get chat rooms"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    try:
        conn = sqlite3.connect('chat_app.db')
        cursor = conn.execute("SELECT id, name, description FROM chat_rooms ORDER BY name")
        rooms = [{"id": row[0], "name": row[1], "description": row[2] or ""} for row in cursor.fetchall()]
        conn.close()
        return jsonify(rooms)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/messages/<int:room_id>')
def get_messages(room_id):
    """API endpoint to get messages for a room"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    try:
        conn = sqlite3.connect('chat_app.db')
        cursor = conn.execute('''
            SELECT u.username, m.message, m.message_type, m.timestamp
            FROM messages m
            JOIN users u ON m.user_id = u.id
            WHERE m.room_id = ?
            ORDER BY m.timestamp DESC
            LIMIT 100
        ''', (room_id,))

        messages = []
        for row in cursor.fetchall():
            messages.append({
                "username": row[0],
                "message": row[1],
                "type": row[2],
                "timestamp": row[3]
            })

        conn.close()
        return jsonify(list(reversed(messages)))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/create_room', methods=['POST'])
def create_room():
    """API endpoint to create a new room"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    room_name = data.get('name', '').strip()

    if not room_name:
        return jsonify({"error": "Room name is required"}), 400

    try:
        conn = sqlite3.connect('chat_app.db')
        cursor = conn.execute(
            "INSERT INTO chat_rooms (name, description, created_by) VALUES (?, ?, ?)",
            (room_name, "", session['user_id'])
        )
        room_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({"success": True, "room_id": room_id, "room_name": room_name})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Room name already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    if 'user_id' not in session:
        return False

    print(f"User {session.get('username')} connected")
    join_room('general')  # Join general room by default

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"User {session.get('username')} disconnected")

@socketio.on('join_room')
def handle_join_room(data):
    """Handle joining a room"""
    room_name = data.get('room')
    if room_name:
        leave_room(session.get('current_room', 'general'))
        join_room(room_name)
        session['current_room'] = room_name
        emit('room_joined', {'room': room_name})

@socketio.on('send_message')
def handle_message(data):
    """Handle incoming message"""
    message = data.get('message', '').strip()
    room = data.get('room', 'general')

    if not message or 'user_id' not in session:
        return

    # Process emojis
    for emoji_code, emoji_char in EMOJI_MAP.items():
        message = message.replace(emoji_code, emoji_char)

    username = session.get('username')

    # Save to database
    try:
        conn = sqlite3.connect('chat_app.db')
        # Get room ID
        cursor = conn.execute("SELECT id FROM chat_rooms WHERE name = ?", (room,))
        room_row = cursor.fetchone()
        if room_row:
            room_id = room_row[0]
            conn.execute(
                "INSERT INTO messages (room_id, user_id, username, message) VALUES (?, ?, ?, ?)",
                (room_id, session['user_id'], username, message)
            )
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving message: {e}")

    # Broadcast message to room
    emit('new_message', {
        'username': username,
        'message': message,
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'room': room
    }, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=3200, allow_unsafe_werkzeug=True)
