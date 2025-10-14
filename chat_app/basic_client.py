#!/usr/bin/env python3
"""
Basic Chat Client - Text-based chat application for beginners
Oasis Infobyte Summer Internship Program

This client connects to the chat server and allows real-time messaging.
"""

import socket
import threading
import sys
import os
import select

class ChatClient:
    def __init__(self, host='localhost', port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.username = ""
        self.running = False

    def connect(self):
        """Connect to the chat server"""
        try:
            self.client.connect((self.host, self.port))
            print(f"[CLIENT] Connected to server at {self.host}:{self.port}")

            # Get username (this was already handled by server in our implementation)
            # In a real implementation, you might want to handle this differently
            return True
        except Exception as e:
            print(f"[CLIENT] Failed to connect to server: {e}")
            return False

    def start(self):
        """Start the chat client"""
        if not self.connect():
            return

        self.running = True

        # Start thread to receive messages
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

        # Main loop for sending messages
        self.send_messages()

    def receive_messages(self):
        """Continuously receive messages from server"""
        while self.running:
            try:
                # Use select to check if data is available
                ready, _, _ = select.select([self.client], [], [], 0.1)

                if ready:
                    message = self.client.recv(1024).decode('utf-8')
                    if message:
                        print(message, end='', flush=True)
                    else:
                        print("\n[CLIENT] Connection to server lost.")
                        self.running = False
                        break

            except (ConnectionResetError, BrokenPipeError):
                print("\n[CLIENT] Connection to server lost.")
                self.running = False
                break
            except Exception as e:
                if self.running:
                    print(f"\n[CLIENT] Error receiving message: {e}")
                break

    def send_messages(self):
        """Send messages to server"""
        print("Type your messages below. Type 'quit' to exit.")
        print("-" * 50)

        try:
            while self.running:
                message = input()

                if message.lower() == 'quit':
                    self.running = False
                    break

                if message.strip():
                    try:
                        self.client.send(message.encode('utf-8'))
                    except (ConnectionResetError, BrokenPipeError):
                        print("[CLIENT] Failed to send message. Connection lost.")
                        self.running = False
                        break

        except KeyboardInterrupt:
            print("\n[CLIENT] Disconnecting...")
            self.running = False
        finally:
            self.disconnect()

    def disconnect(self):
        """Disconnect from server"""
        self.running = False
        try:
            self.client.close()
        except:
            pass
        print("[CLIENT] Disconnected from server.")

def main():
    """Main function to run the chat client"""
    if len(sys.argv) < 2:
        print("Usage: python basic_client.py <server_ip> [port]")
        sys.exit(1)

    server_ip = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5555

    client = ChatClient(host=server_ip, port=port)
    client.start()

if __name__ == "__main__":
    main()
