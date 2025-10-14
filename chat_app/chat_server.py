#!/usr/bin/env python3
"""
Enhanced Chat Server - Supports both basic text and GUI clients
Oasis Infobyte Summer Internship Program

This server handles multiple clients and supports both simple text protocol
and JSON protocol for advanced GUI clients.
"""

import socket
import threading
import sys
import os
import json
import sqlite3
from datetime import datetime

class EnhancedChatServer:
    def __init__(self, host='localhost', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.host = host
        self.port = port
        self.clients = []
        self.client_info = {}  # Maps socket -> client info
        self.rooms = {}  # Room management

        # Setup database for message history
        self.setup_database()

    def setup_database(self):
        """Initialize SQLite database for message history"""
        self.db_path = "chat_server.db"
        conn = sqlite3.connect(self.db_path)

        # Create rooms table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create messages table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_name TEXT NOT NULL,
                username TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create default general room
        try:
            conn.execute("INSERT OR IGNORE INTO rooms (name) VALUES (?)", ("general",))
            conn.commit()
        except:
            pass

        conn.close()

    def start(self):
        """Start the chat server"""
        try:
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            print(f"[SERVER] Enhanced chat server started on {self.host}:{self.port}")
            print("[SERVER] Waiting for connections...")

            # Load existing rooms
            self.load_rooms()

            while True:
                client_socket, client_address = self.server.accept()
                print(f"[SERVER] New connection from {client_address}")

                # Start a new thread for each client
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.daemon = True
                client_thread.start()

        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down server...")
        except Exception as e:
            print(f"[SERVER] Error: {e}")
        finally:
            self.shutdown()

    def load_rooms(self):
        """Load existing chat rooms from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("SELECT name FROM rooms")
            rooms = cursor.fetchall()
            conn.close()

            for (room_name,) in rooms:
                self.rooms[room_name] = []

        except Exception as e:
            print(f"[SERVER] Error loading rooms: {e}")

    def handle_client(self, client_socket, client_address):
        """Handle individual client connections"""
        try:
            # Add client to the list
            self.clients.append(client_socket)
            self.client_info[client_socket] = {
                'address': client_address,
                'username': f"User_{client_address[1]}",
                'room': 'general',
                'protocol': 'text'  # Default to text protocol
            }

            # Add to general room
            if 'general' not in self.rooms:
                self.rooms['general'] = []
            self.rooms['general'].append(client_socket)

            # Send welcome message
            welcome_msg = "\n[SERVER] Welcome to the Enhanced Chat Server!\n"
            welcome_msg += "[SERVER] Use '/help' for commands or connect with GUI client for advanced features.\n"
            client_socket.send(welcome_msg.encode('utf-8'))

            # Broadcast user joined
            self.broadcast(f"[SERVER] {self.client_info[client_socket]['username']} has joined the chat!",
                          client_socket, 'general')

            while True:
                try:
                    # Check if data is available
                    data = self.receive_data(client_socket)
                    if not data:
                        break

                    # Determine protocol based on message format
                    if data.strip().startswith('{'):
                        # JSON protocol (GUI client)
                        self.handle_json_message(client_socket, data)
                    else:
                        # Text protocol (basic client)
                        self.handle_text_message(client_socket, data)

                except (ConnectionResetError, BrokenPipeError):
                    break

        except Exception as e:
            print(f"[SERVER] Error handling client {client_address}: {e}")
        finally:
            self.remove_client(client_socket)

    def receive_data(self, client_socket):
        """Receive data from client, handling both text and JSON protocols"""
        try:
            # Try to receive a line (for JSON protocol)
            data = client_socket.recv(4096).decode('utf-8')

            # Check if it's a complete JSON message or partial
            if data.strip().startswith('{'):
                # Look for complete JSON objects
                messages = []
                current = ""
                brace_count = 0

                for char in data:
                    current += char
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            messages.append(current.strip())
                            current = ""

                # Handle any remaining partial JSON
                if current.strip():
                    # For now, just handle complete messages
                    pass

                return messages[0] if messages else None
            else:
                # Text protocol - split by lines
                return data

        except UnicodeDecodeError:
            return None
        except Exception as e:
            print(f"[SERVER] Error receiving data: {e}")
            return None

    def handle_json_message(self, client_socket, data):
        """Handle JSON protocol messages from GUI clients"""
        try:
            message_data = json.loads(data)
            msg_type = message_data.get('type')
            username = message_data.get('username', 'Unknown')
            room_name = message_data.get('room_id', 'general')

            # Update client info
            self.client_info[client_socket]['username'] = username
            self.client_info[client_socket]['protocol'] = 'json'

            if msg_type == 'message':
                message = message_data.get('message', '')
                self.handle_chat_message(client_socket, username, message, room_name)

        except json.JSONDecodeError:
            print(f"[SERVER] Invalid JSON received: {data}")
        except Exception as e:
            print(f"[SERVER] Error handling JSON message: {e}")

    def handle_text_message(self, client_socket, data):
        """Handle text protocol messages from basic clients"""
        lines = data.strip().split('\n')
        for line in lines:
            if not line:
                continue

            # Handle commands
            if line.startswith('/'):
                self.handle_command(client_socket, line)
            else:
                # Regular chat message
                username = self.client_info[client_socket]['username']
                current_room = self.client_info[client_socket]['room']
                self.handle_chat_message(client_socket, username, line, current_room)

    def handle_command(self, client_socket, command):
        """Handle text commands"""
        parts = command[1:].split()
        if not parts:
            return

        cmd = parts[0].lower()

        if cmd == 'help':
            help_msg = "\n[SERVER] Available commands:\n"
            help_msg += "/help - Show this help\n"
            help_msg += "/rooms - List available rooms\n"
            help_msg += "/join <room> - Join a chat room\n"
            help_msg += "/create <room> - Create a new room\n"
            help_msg += "/users - List users in current room\n"
            help_msg += "/quit - Disconnect\n"
            client_socket.send(help_msg.encode('utf-8'))

        elif cmd == 'rooms':
            room_list = "\n[SERVER] Available rooms:\n" + "\n".join(self.rooms.keys())
            client_socket.send(room_list.encode('utf-8'))

        elif cmd == 'join' and len(parts) > 1:
            room_name = parts[1]
            self.join_room(client_socket, room_name)

        elif cmd == 'create' and len(parts) > 1:
            room_name = parts[1]
            self.create_room(client_socket, room_name)

        elif cmd == 'users':
            current_room = self.client_info[client_socket]['room']
            users = [self.client_info[c]['username'] for c in self.rooms.get(current_room, [])]
            user_list = f"\n[SERVER] Users in {current_room}: {', '.join(users)}\n"
            client_socket.send(user_list.encode('utf-8'))

        elif cmd == 'quit':
            client_socket.send(b"[SERVER] Goodbye!\n")
            return False  # Signal to disconnect

        return True

    def join_room(self, client_socket, room_name):
        """Join a chat room"""
        if room_name not in self.rooms:
            client_socket.send(f"[SERVER] Room '{room_name}' does not exist.\n".encode('utf-8'))
            return

        # Remove from current room
        current_room = self.client_info[client_socket]['room']
        if client_socket in self.rooms.get(current_room, []):
            self.rooms[current_room].remove(client_socket)

        # Add to new room
        self.rooms[room_name].append(client_socket)
        self.client_info[client_socket]['room'] = room_name

        client_socket.send(f"[SERVER] Joined room '{room_name}'\n".encode('utf-8'))

        # Broadcast to new room
        self.broadcast(f"[SERVER] {self.client_info[client_socket]['username']} joined the room",
                      client_socket, room_name)

    def create_room(self, client_socket, room_name):
        """Create a new chat room"""
        if room_name in self.rooms:
            client_socket.send(f"[SERVER] Room '{room_name}' already exists.\n".encode('utf-8'))
            return

        # Create room in database
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("INSERT INTO rooms (name) VALUES (?)", (room_name,))
            conn.commit()
            conn.close()
        except Exception as e:
            client_socket.send(f"[SERVER] Failed to create room: {e}\n".encode('utf-8'))
            return

        # Create room in memory
        self.rooms[room_name] = [client_socket]
        self.client_info[client_socket]['room'] = room_name

        client_socket.send(f"[SERVER] Created and joined room '{room_name}'\n".encode('utf-8'))

    def handle_chat_message(self, client_socket, username, message, room_name):
        """Handle regular chat messages"""
        # Save to database
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                "INSERT INTO messages (room_name, username, message) VALUES (?, ?, ?)",
                (room_name, username, message)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[SERVER] Error saving message: {e}")

        # Broadcast to room
        self.broadcast(f"[{username}] {message}", client_socket, room_name)

    def broadcast(self, message, sender_socket, room_name):
        """Broadcast message to all clients in a room except sender"""
        if room_name not in self.rooms:
            return

        for client in self.rooms[room_name][:]:  # Create a copy
            if client != sender_socket:
                try:
                    # Format message based on client protocol
                    if self.client_info[client]['protocol'] == 'json':
                        # Send as JSON for GUI clients
                        json_msg = {
                            'type': 'message',
                            'username': 'Server' if message.startswith('[SERVER]') else message.split(']')[0][1:],
                            'message': message,
                            'room_id': room_name
                        }
                        client.send((json.dumps(json_msg) + '\n').encode('utf-8'))
                    else:
                        # Send as plain text for basic clients
                        client.send(message.encode('utf-8'))
                except (ConnectionResetError, BrokenPipeError):
                    # Remove broken connections
                    self.remove_client(client)

    def remove_client(self, client_socket):
        """Remove a client from the server"""
        if client_socket in self.clients:
            username = self.client_info[client_socket]['username']
            room_name = self.client_info[client_socket]['room']

            # Remove from room
            if room_name in self.rooms and client_socket in self.rooms[room_name]:
                self.rooms[room_name].remove(client_socket)

            # Remove from clients list
            self.clients.remove(client_socket)
            del self.client_info[client_socket]

            try:
                client_socket.close()
            except:
                pass

            # Broadcast user left
            self.broadcast(f"[SERVER] {username} has left the chat.", None, room_name)

    def shutdown(self):
        """Shutdown the server"""
        print("[SERVER] Closing all connections...")
        for client in self.clients[:]:
            self.remove_client(client)

        try:
            self.server.close()
        except:
            pass

        print("[SERVER] Server shutdown complete.")

def main():
    """Main function to run the chat server"""
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 5555

    server = EnhancedChatServer(port=port)
    server.start()

if __name__ == "__main__":
    main()
