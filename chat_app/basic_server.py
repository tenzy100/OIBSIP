#!/usr/bin/env python3
"""
Basic Chat Server - Text-based chat application for beginners
Oasis Infobyte Summer Internship Program

This server handles multiple clients and broadcasts messages between them.
"""

import socket
import threading
import sys
import os

class ChatServer:
    def __init__(self, host='localhost', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.host = host
        self.port = port
        self.clients = []
        self.client_names = {}

    def start(self):
        """Start the chat server"""
        try:
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            print(f"[SERVER] Chat server started on {self.host}:{self.port}")
            print("[SERVER] Waiting for connections...")

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

    def handle_client(self, client_socket, client_address):
        """Handle individual client connections"""
        try:
            # Request username
            client_socket.send("Enter your username: ".encode('utf-8'))
            username = client_socket.recv(1024).decode('utf-8').strip()

            if not username:
                username = f"User_{client_address[1]}"

            # Add client to the list
            self.clients.append(client_socket)
            self.client_names[client_socket] = username

            # Welcome message
            welcome_msg = f"\n[SERVER] Welcome {username}! You are now connected to the chat.\n"
            client_socket.send(welcome_msg.encode('utf-8'))

            # Notify others about new user
            self.broadcast(f"[SERVER] {username} has joined the chat!", client_socket)

            while True:
                try:
                    message = client_socket.recv(1024).decode('utf-8')
                    if not message:
                        break

                    # Broadcast message to all clients except sender
                    full_message = f"[{username}] {message}"
                    self.broadcast(full_message, client_socket)

                except ConnectionResetError:
                    break

        except Exception as e:
            print(f"[SERVER] Error handling client {client_address}: {e}")
        finally:
            self.remove_client(client_socket)

    def broadcast(self, message, sender_socket=None):
        """Broadcast message to all connected clients"""
        for client in self.clients[:]:  # Create a copy to avoid modification during iteration
            if client != sender_socket:
                try:
                    client.send(message.encode('utf-8'))
                except:
                    # Remove broken connections
                    self.remove_client(client)

    def remove_client(self, client_socket):
        """Remove a client from the server"""
        if client_socket in self.clients:
            username = self.client_names.get(client_socket, "Unknown")
            self.clients.remove(client_socket)
            del self.client_names[client_socket]

            try:
                client_socket.close()
            except:
                pass

            # Notify others about user leaving
            self.broadcast(f"[SERVER] {username} has left the chat.")

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

    server = ChatServer(port=port)
    server.start()

if __name__ == "__main__":
    main()
