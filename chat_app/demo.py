#!/usr/bin/env python3
"""
Chat Application Demo Script
Oasis Infobyte Summer Internship Program

This script demonstrates how to run both the basic and advanced chat applications.
Run this script to see usage instructions and test the applications.
"""

import os
import sys
import subprocess
import time

def print_header():
    """Print application header"""
    print("=" * 60)
    print("CHAT APPLICATION DEMO")
    print("Oasis Infobyte Summer Internship Program")
    print("=" * 60)
    print()

def print_menu():
    """Print main menu"""
    print("Choose a demo option:")
    print("1. Basic Chat Application (Beginner)")
    print("2. Advanced GUI Chat Application")
    print("3. Mixed Mode (Basic + GUI clients)")
    print("4. View README")
    print("5. Exit")
    print()

def run_basic_demo():
    """Run basic chat application demo"""
    print("BASIC CHAT APPLICATION DEMO")
    print("-" * 40)
    print("This demo will start the server and show how to connect clients.")
    print()
    print("Steps:")
    print("1. Starting server...")
    print("2. You can open new terminals to run clients")
    print("3. Press Ctrl+C to stop the server")
    print()

    try:
        # Start server in background
        print("Starting server on port 5555...")
        server_process = subprocess.Popen([sys.executable, "basic_server.py", "5555"])

        print("Server started! PID:", server_process.pid)
        print()
        print("USAGE INSTRUCTIONS:")
        print("- Terminal 1 (current): Server is running")
        print("- Terminal 2: python basic_client.py localhost 5555")
        print("- Terminal 3: python basic_client.py localhost 5555")
        print()
        print("Commands in client:")
        print("- Type messages and press Enter to send")
        print("- Type '/help' for commands")
        print("- Type '/quit' to exit")
        print()

        # Wait for user to stop
        input("Press Enter to stop the server...")
        server_process.terminate()
        server_process.wait()

    except KeyboardInterrupt:
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()
    except Exception as e:
        print(f"Error: {e}")

def run_gui_demo():
    """Run GUI chat application demo"""
    print("ADVANCED GUI CHAT APPLICATION DEMO")
    print("-" * 40)
    print("This demo will start the enhanced server and GUI client.")
    print()

    try:
        # Start enhanced server
        print("Starting enhanced server on port 5555...")
        server_process = subprocess.Popen([sys.executable, "chat_server.py", "5555"])

        print("Server started! PID:", server_process.pid)
        print("Starting GUI client...")
        print()

        # Start GUI client
        gui_process = subprocess.Popen([sys.executable, "gui_chat_app.py"])

        print("GUI client started! PID:", gui_process.pid)
        print()
        print("The GUI application should open in a new window.")
        print("You can:")
        print("- Register a new account or login")
        print("- Create or join chat rooms")
        print("- Send messages with emoji support")
        print("- Share files")
        print("- View message history")
        print()

        # Wait for GUI to close
        gui_process.wait()

        # Stop server
        print("Stopping server...")
        server_process.terminate()
        server_process.wait()

    except Exception as e:
        print(f"Error: {e}")

def run_mixed_demo():
    """Run mixed mode demo"""
    print("MIXED MODE DEMO")
    print("-" * 40)
    print("This demo shows both basic and GUI clients connecting to the same server.")
    print()

    try:
        # Start enhanced server
        print("Starting enhanced server on port 5555...")
        server_process = subprocess.Popen([sys.executable, "chat_server.py", "5555"])

        print("Server started! PID:", server_process.pid)
        print()
        print("Now you can:")
        print("1. Start basic clients: python basic_client.py localhost 5555")
        print("2. Start GUI client: python gui_chat_app.py")
        print("3. All clients will be able to communicate!")
        print()

        # Wait for user input
        input("Press Enter when you're done testing...")
        server_process.terminate()
        server_process.wait()

    except Exception as e:
        print(f"Error: {e}")

def show_readme():
    """Show README content"""
    try:
        with open("README.md", "r") as f:
            print(f.read())
    except FileNotFoundError:
        print("README.md not found!")

def main():
    """Main demo function"""
    print_header()

    while True:
        print_menu()
        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            run_basic_demo()
        elif choice == "2":
            run_gui_demo()
        elif choice == "3":
            run_mixed_demo()
        elif choice == "4":
            show_readme()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice! Please try again.")
        print()

if __name__ == "__main__":
    main()
