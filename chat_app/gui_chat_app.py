#!/usr/bin/env python3
"""
Advanced GUI Chat Application
Oasis Infobyte Summer Internship Program

A comprehensive chat application with GUI, user authentication,
multiple chat rooms, message history, emoji support, and file sharing.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import socket
import threading
import json
import os
import base64
import time
from datetime import datetime
import hashlib
import secrets
import sqlite3
from pathlib import Path

class ChatApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Advanced Chat Application")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)

        # Initialize variables
        self.current_user = None
        self.chat_rooms = {}
        self.current_room = None
        self.client_socket = None
        self.connected = False
        self.message_history = []
        self.emoji_map = self.load_emojis()

        # Setup GUI
        self.setup_database()
        self.create_login_window()

    def setup_database(self):
        """Initialize SQLite database for user data and message history"""
        self.db_path = "chat_app.db"
        conn = sqlite3.connect(self.db_path)

        # Create users table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create chat_rooms table
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

        # Create messages table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                message TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                file_path TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_id) REFERENCES chat_rooms (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Create user_rooms table for room membership
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                room_id INTEGER NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (room_id) REFERENCES chat_rooms (id),
                UNIQUE(user_id, room_id)
            )
        ''')

        conn.commit()
        conn.close()

    def load_emojis(self):
        """Load emoji mappings"""
        return {
            ":smile:": "😊", ":laugh:": "😂", ":wink:": "😉", ":heart:": "❤️",
            ":thumbs_up:": "👍", ":thumbs_down:": "👎", ":clap:": "👏", ":pray:": "🙏",
            ":fire:": "🔥", ":100:": "💯", ":party:": "🎉", ":rocket:": "🚀",
            ":sun:": "☀️", ":moon:": "🌙", ":star:": "⭐", ":rainbow:": "🌈",
            ":pizza:": "🍕", ":coffee:": "☕", ":beer:": "🍺", ":cake:": "🎂"
        }

    def hash_password(self, password, salt=None):
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)

        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return pwd_hash.hex(), salt

    def verify_password(self, password, stored_hash, salt):
        """Verify password against stored hash"""
        pwd_hash, _ = self.hash_password(password, salt)
        return pwd_hash == stored_hash

    def create_login_window(self):
        """Create login/registration window"""
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Login - Advanced Chat App")
        self.login_window.geometry("400x500")
        self.login_window.resizable(False, False)

        # Center the window
        self.login_window.transient(self.root)
        self.login_window.grab_set()

        # Main frame
        main_frame = ttk.Frame(self.login_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="Advanced Chat Application",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # Login frame
        login_frame = ttk.LabelFrame(main_frame, text="Login", padding="15")
        login_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.login_username = ttk.Entry(login_frame, width=30)
        self.login_username.grid(row=0, column=1, pady=5, padx=(10, 0))

        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.login_password = ttk.Entry(login_frame, show="*", width=30)
        self.login_password.grid(row=1, column=1, pady=5, padx=(10, 0))

        # Login button
        login_btn = ttk.Button(login_frame, text="Login", command=self.login)
        login_btn.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        # Registration frame
        reg_frame = ttk.LabelFrame(main_frame, text="Register", padding="15")
        reg_frame.pack(fill=tk.X, pady=(15, 0))

        ttk.Label(reg_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.reg_username = ttk.Entry(reg_frame, width=30)
        self.reg_username.grid(row=0, column=1, pady=5, padx=(10, 0))

        ttk.Label(reg_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.reg_password = ttk.Entry(reg_frame, show="*", width=30)
        self.reg_password.grid(row=1, column=1, pady=5, padx=(10, 0))

        ttk.Label(reg_frame, text="Confirm Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.reg_confirm = ttk.Entry(reg_frame, show="*", width=30)
        self.reg_confirm.grid(row=2, column=1, pady=5, padx=(10, 0))

        # Register button
        reg_btn = ttk.Button(reg_frame, text="Register", command=self.register)
        reg_btn.grid(row=3, column=0, columnspan=2, pady=(10, 0))

        # Status label
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=(10, 0))

        # Focus on username field
        self.login_username.focus()

    def login(self):
        """Handle user login"""
        username = self.login_username.get().strip()
        password = self.login_password.get()

        if not username or not password:
            self.status_label.config(text="Please enter both username and password")
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT id, password_hash, salt FROM users WHERE username = ?", (username,))

        user = cursor.fetchone()
        conn.close()

        if user and self.verify_password(password, user[1], user[2]):
            self.current_user = {"id": user[0], "username": username}
            self.status_label.config(text=f"Login successful! Welcome, {username}")
            self.login_window.after(1000, self.show_main_window)
        else:
            self.status_label.config(text="Invalid username or password")

    def register(self):
        """Handle user registration"""
        username = self.reg_username.get().strip()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()

        if not username or not password or not confirm:
            self.status_label.config(text="Please fill in all fields")
            return

        if password != confirm:
            self.status_label.config(text="Passwords do not match")
            return

        if len(password) < 6:
            self.status_label.config(text="Password must be at least 6 characters")
            return

        # Hash password
        password_hash, salt = self.hash_password(password)

        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                (username, password_hash, salt)
            )
            conn.commit()
            conn.close()

            self.status_label.config(text=f"Registration successful! You can now login as {username}")
        except sqlite3.IntegrityError:
            self.status_label.config(text="Username already exists")
        except Exception as e:
            self.status_label.config(text=f"Registration failed: {e}")

    def show_main_window(self):
        """Show main chat window"""
        self.login_window.destroy()
        self.create_main_window()

    def create_main_window(self):
        """Create main chat application window"""
        # Configure main window
        self.root.deiconify()

        # Create menu bar
        self.create_menu_bar()

        # Create main layout
        self.create_main_layout()

        # Load default chat rooms
        self.load_chat_rooms()

        # Connect to server
        self.connect_to_server()

    def create_menu_bar(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Chat Room", command=self.create_chat_room)
        file_menu.add_command(label="Join Chat Room", command=self.join_chat_room)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear Chat", command=self.clear_chat)
        edit_menu.add_command(label="Message History", command=self.show_message_history)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Emoji Panel", command=self.show_emoji_panel)
        tools_menu.add_command(label="Send File", command=self.send_file)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_main_layout(self):
        """Create main chat interface layout"""
        # Main paned window
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left sidebar (rooms and users)
        self.sidebar = ttk.Frame(self.main_paned, width=250, relief=tk.RIDGE)
        self.main_paned.add(self.sidebar, weight=0)

        # Right side (chat area)
        self.chat_area = ttk.Frame(self.main_paned, relief=tk.RIDGE)
        self.main_paned.add(self.chat_area, weight=1)

        # Create sidebar content
        self.create_sidebar()

        # Create chat area
        self.create_chat_area()

    def create_sidebar(self):
        """Create sidebar with rooms and users"""
        # User info at top
        user_frame = ttk.Frame(self.sidebar)
        user_frame.pack(fill=tk.X, padx=5, pady=5)

        self.user_label = ttk.Label(user_frame, text=f"Logged in as: {self.current_user['username']}")
        self.user_label.pack(anchor=tk.W)

        # Chat rooms section
        rooms_frame = ttk.LabelFrame(self.sidebar, text="Chat Rooms", padding="5")
        rooms_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Rooms listbox with scrollbar
        rooms_scrollbar = ttk.Scrollbar(rooms_frame)
        rooms_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.rooms_listbox = tk.Listbox(rooms_frame, yscrollcommand=rooms_scrollbar.set,
                                       selectmode=tk.SINGLE)
        self.rooms_listbox.pack(fill=tk.BOTH, expand=True)
        rooms_scrollbar.config(command=self.rooms_listbox.yview)

        # Bind room selection
        self.rooms_listbox.bind('<<ListboxSelect>>', self.on_room_select)

        # Room controls
        room_controls = ttk.Frame(self.sidebar)
        room_controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(room_controls, text="Join Room", command=self.join_chat_room).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(room_controls, text="Create Room", command=self.create_chat_room).pack(fill=tk.X)

    def create_chat_area(self):
        """Create main chat area"""
        # Chat display area
        chat_display_frame = ttk.LabelFrame(self.chat_area, text="Chat", padding="5")
        chat_display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Chat text widget with scrollbar
        chat_scrollbar = ttk.Scrollbar(chat_display_frame)
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chat_text = tk.Text(chat_display_frame, wrap=tk.WORD, yscrollcommand=chat_scrollbar.set,
                                state=tk.DISABLED, font=("Arial", 10))
        self.chat_text.pack(fill=tk.BOTH, expand=True)
        chat_scrollbar.config(command=self.chat_text.yview)

        # Message input area
        input_frame = ttk.Frame(self.chat_area)
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        # Message input
        self.message_input = tk.Text(input_frame, height=3, wrap=tk.WORD, font=("Arial", 10))
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Send button
        send_btn = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # Bind Enter key to send message
        self.message_input.bind('<Return>', self.send_message_on_enter)
        self.message_input.bind('<Shift-Return>', self.insert_newline)

        # Status bar
        self.status_bar = ttk.Label(self.root, text="Not connected", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_chat_rooms(self):
        """Load available chat rooms"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("SELECT id, name, description FROM chat_rooms ORDER BY name")
            rooms = cursor.fetchall()
            conn.close()

            self.rooms_listbox.delete(0, tk.END)
            self.chat_rooms.clear()

            for room_id, name, description in rooms:
                self.rooms_listbox.insert(tk.END, name)
                self.chat_rooms[name] = {
                    'id': room_id,
                    'description': description or ""
                }

        except Exception as e:
            print(f"Error loading chat rooms: {e}")

    def on_room_select(self, event):
        """Handle room selection"""
        selection = self.rooms_listbox.curselection()
        if selection:
            room_name = self.rooms_listbox.get(selection[0])
            self.switch_to_room(room_name)

    def switch_to_room(self, room_name):
        """Switch to selected chat room"""
        if room_name in self.chat_rooms:
            self.current_room = self.chat_rooms[room_name]

            # Update chat display title
            room_title = f"Chat - {room_name}"
            # Find the LabelFrame containing the chat and update its text
            for child in self.chat_area.winfo_children():
                if isinstance(child, ttk.LabelFrame) and child.cget('text') == 'Chat':
                    child.config(text=room_title)
                    break

            # Load message history for this room
            self.load_message_history()

            # Update status
            self.status_bar.config(text=f"Switched to room: {room_name}")

    def load_message_history(self):
        """Load message history for current room"""
        if not self.current_room:
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute('''
                SELECT u.username, m.message, m.message_type, m.file_path, m.timestamp
                FROM messages m
                JOIN users u ON m.user_id = u.id
                WHERE m.room_id = ?
                ORDER BY m.timestamp
            ''', (self.current_room['id'],))

            messages = cursor.fetchall()
            conn.close()

            # Clear current chat
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.delete(1.0, tk.END)

            # Add messages to chat
            for username, message, msg_type, file_path, timestamp in messages:
                timestamp_str = datetime.fromisoformat(timestamp).strftime("%H:%M")
                if msg_type == 'text':
                    self.chat_text.insert(tk.END, f"[{timestamp_str}] {username}: {message}\n")
                elif msg_type == 'file':
                    self.chat_text.insert(tk.END, f"[{timestamp_str}] {username}: 📎 {message}\n")

            self.chat_text.config(state=tk.DISABLED)
            self.chat_text.see(tk.END)

        except Exception as e:
            print(f"Error loading message history: {e}")

    def send_message(self):
        """Send message to current room"""
        message = self.message_input.get(1.0, tk.END).strip()
        if not message or not self.current_room or not self.connected:
            return

        # Process emojis
        for emoji_code, emoji_char in self.emoji_map.items():
            message = message.replace(emoji_code, emoji_char)

        # Send to server (in a real implementation)
        self.send_to_server({
            'type': 'message',
            'room_id': self.current_room['id'],
            'message': message,
            'username': self.current_user['username']
        })

        # Add to local chat display
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"[{timestamp}] {self.current_user['username']}: {message}\n")
        self.chat_text.config(state=tk.DISABLED)
        self.chat_text.see(tk.END)

        # Save to database
        self.save_message(message, 'text')

        # Clear input
        self.message_input.delete(1.0, tk.END)

    def send_message_on_enter(self, event):
        """Send message when Enter is pressed"""
        self.send_message()
        return 'break'  # Prevent default behavior

    def insert_newline(self, event):
        """Insert newline when Shift+Enter is pressed"""
        self.message_input.insert(tk.INSERT, '\n')
        return 'break'

    def save_message(self, message, msg_type, file_path=None):
        """Save message to database"""
        if not self.current_room:
            return

        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT INTO messages (room_id, user_id, username, message, message_type, file_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.current_room['id'], self.current_user['id'], self.current_user['username'],
                  message, msg_type, file_path))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving message: {e}")

    def send_to_server(self, data):
        """Send data to server"""
        if self.connected and self.client_socket:
            try:
                message = json.dumps(data) + '\n'
                self.client_socket.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error sending to server: {e}")
                self.connected = False
                self.status_bar.config(text="Connection lost")

    def connect_to_server(self):
        """Connect to chat server"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(('localhost', 5555))  # Connect to basic server for now
            self.connected = True
            self.status_bar.config(text="Connected to server")

            # Start listening for messages
            threading.Thread(target=self.listen_for_messages, daemon=True).start()

        except Exception as e:
            self.status_bar.config(text=f"Failed to connect: {e}")
            self.connected = False

    def listen_for_messages(self):
        """Listen for incoming messages from server"""
        while self.connected:
            try:
                data = self.client_socket.recv(1024).decode('utf-8').strip()
                if data:
                    # Process incoming message
                    try:
                        message_data = json.loads(data)
                        self.handle_incoming_message(message_data)
                    except json.JSONDecodeError:
                        # Handle plain text messages from basic server
                        self.display_message("Server", data)
            except:
                break

        self.connected = False
        self.status_bar.config(text="Disconnected from server")

    def handle_incoming_message(self, data):
        """Handle incoming message data"""
        if data['type'] == 'message':
            username = data['username']
            message = data['message']

            # Add to chat display
            self.display_message(username, message)

            # Save to database if it's for current room
            if self.current_room and data.get('room_id') == self.current_room['id']:
                self.save_message(message, 'text')

    def display_message(self, username, message):
        """Display message in chat"""
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"[{timestamp}] {username}: {message}\n")
        self.chat_text.config(state=tk.DISABLED)
        self.chat_text.see(tk.END)

    def create_chat_room(self):
        """Create a new chat room"""
        room_name = simpledialog.askstring("Create Room", "Enter room name:")
        if room_name:
            room_name = room_name.strip()
            if room_name:
                try:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.execute(
                        "INSERT INTO chat_rooms (name, description, created_by) VALUES (?, ?, ?)",
                        (room_name, "", self.current_user['id'])
                    )
                    room_id = cursor.lastrowid
                    conn.commit()
                    conn.close()

                    # Add to rooms list
                    self.rooms_listbox.insert(tk.END, room_name)
                    self.chat_rooms[room_name] = {'id': room_id, 'description': ""}

                    messagebox.showinfo("Success", f"Chat room '{room_name}' created successfully!")

                except sqlite3.IntegrityError:
                    messagebox.showerror("Error", "Room name already exists!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create room: {e}")

    def join_chat_room(self):
        """Join an existing chat room"""
        # For now, just show available rooms
        if self.rooms_listbox.size() > 0:
            messagebox.showinfo("Join Room", "Select a room from the list and click on it to join.")
        else:
            messagebox.showinfo("No Rooms", "No chat rooms available. Create one first!")

    def clear_chat(self):
        """Clear current chat display"""
        if messagebox.askyesno("Clear Chat", "Are you sure you want to clear the chat?"):
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.delete(1.0, tk.END)
            self.chat_text.config(state=tk.DISABLED)

    def show_message_history(self):
        """Show message history window"""
        history_window = tk.Toplevel(self.root)
        history_window.title("Message History")
        history_window.geometry("800x600")

        # Create text widget for history
        text = tk.Text(history_window, wrap=tk.WORD, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(history_window, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)

        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Load and display history
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute('''
                SELECT r.name, u.username, m.message, m.timestamp
                FROM messages m
                JOIN users u ON m.user_id = u.id
                JOIN chat_rooms r ON m.room_id = r.id
                ORDER BY m.timestamp DESC
                LIMIT 1000
            ''')

            messages = cursor.fetchall()
            conn.close()

            text.insert(tk.END, "=== MESSAGE HISTORY (Last 1000 messages) ===\n\n")
            for room_name, username, message, timestamp in messages:
                timestamp_str = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M")
                text.insert(tk.END, f"[{timestamp_str}] {room_name} - {username}: {message}\n")

        except Exception as e:
            text.insert(tk.END, f"Error loading history: {e}")

        text.config(state=tk.DISABLED)

    def show_emoji_panel(self):
        """Show emoji selection panel"""
        emoji_window = tk.Toplevel(self.root)
        emoji_window.title("Select Emoji")
        emoji_window.geometry("300x200")

        # Create emoji buttons
        emoji_frame = ttk.Frame(emoji_window)
        emoji_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        row = 0
        col = 0
        for emoji_code, emoji_char in self.emoji_map.items():
            btn = ttk.Button(emoji_frame, text=emoji_char,
                           command=lambda e=emoji_code: self.insert_emoji(e))
            btn.grid(row=row, column=col, padx=2, pady=2)
            col += 1
            if col > 4:
                col = 0
                row += 1

    def insert_emoji(self, emoji_code):
        """Insert emoji code into message input"""
        self.message_input.insert(tk.INSERT, emoji_code)

    def send_file(self):
        """Send file to chat"""
        file_path = filedialog.askopenfilename(
            title="Select file to send",
            filetypes=[
                ("All files", "*.*"),
                ("Images", "*.png;*.jpg;*.jpeg;*.gif"),
                ("Documents", "*.pdf;*.doc;*.docx;*.txt"),
                ("Videos", "*.mp4;*.avi;*.mov"),
                ("Audio", "*.mp3;*.wav")
            ]
        )

        if file_path:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)

            # For demo purposes, just show file info
            message = f"📎 File: {file_name} ({file_size} bytes)"

            self.display_message(self.current_user['username'], message)
            self.save_message(file_name, 'file', file_path)

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About",
                          "Advanced Chat Application\n\n"
                          "Oasis Infobyte Summer Internship Program\n"
                          "A comprehensive chat application with GUI, "
                          "user authentication, multiple chat rooms, "
                          "message history, emoji support, and file sharing.")

    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main function"""
    app = ChatApp()
    app.run()

if __name__ == "__main__":
    main()
