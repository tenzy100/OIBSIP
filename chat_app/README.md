# Chat Application - Oasis Infobyte Summer Internship Program

A comprehensive chat application featuring both basic text-based and advanced GUI implementations.

## Features

### Basic Chat Application (Beginner Level)
- **Text-based interface** using command line
- **Client-server architecture** with socket programming
- **Real-time messaging** between multiple users
- **Simple connection management**

### Advanced GUI Chat Application
- **Modern Tkinter GUI** with intuitive interface
- **User authentication system** (registration/login)
- **Multiple chat rooms** support
- **Message history** storage and retrieval
- **Emoji support** with emoji picker
- **File sharing** capabilities
- **SQLite database** for data persistence
- **JSON protocol** for enhanced communication

## Project Structure

```
chat_app/
├── basic_server.py       # Original basic chat server
├── basic_client.py       # Basic text-based client
├── chat_server.py        # Enhanced server (supports both protocols)
├── gui_chat_app.py       # Advanced GUI application
├── chat_app.db          # SQLite database (created on first run)
├── chat_server.db       # Server database (created on first run)
└── README.md            # This file
```

## Installation & Setup

1. **Navigate to the chat application directory:**
   ```bash
   cd /Users/aryatupkary/OIBSIP/chat_app
   ```

2. **No additional dependencies required** - uses only Python standard library modules

## Usage

### Option 1: Basic Chat Application (Beginner)

1. **Start the basic server:**
   ```bash
   python basic_server.py [port]
   ```
   Default port is 5555.

2. **Start multiple clients (in separate terminals):**
   ```bash
   python basic_client.py <server_ip> [port]
   ```
   - Replace `<server_ip>` with the server IP address (use `localhost` for local testing)
   - Default port is 5555

3. **Chat away!** Type messages and press Enter to send.

### Option 2: Enhanced Chat Application (Advanced)

1. **Start the enhanced server:**
   ```bash
   python chat_server.py [port]
   ```
   Default port is 5555.

2. **Start the GUI client:**
   ```bash
   python gui_chat_app.py
   ```

3. **Register/Login** using the GUI interface

4. **Create or join chat rooms** and start chatting!

### Option 3: Mixed Mode (Basic + GUI Clients)

1. **Start the enhanced server** (supports both protocols)

2. **Connect basic clients** using `basic_client.py`

3. **Connect GUI clients** using `gui_chat_app.py`

4. **All clients can communicate** with each other!

## Commands (Basic Client)

When using the basic text client, you can use these commands:

- `/help` - Show available commands
- `/rooms` - List available chat rooms
- `/join <room>` - Join a specific chat room
- `/create <room>` - Create a new chat room
- `/users` - List users in current room
- `/quit` - Disconnect from server

## GUI Features

### Authentication
- **User Registration:** Create new accounts with username/password
- **Secure Login:** Password hashing with salt
- **Session Management:** Persistent login state

### Chat Rooms
- **Create Rooms:** Start new chat rooms
- **Join Rooms:** Browse and join existing rooms
- **Room Management:** Automatic room creation and cleanup

### Message Features
- **Real-time Messaging:** Instant message delivery
- **Message History:** Persistent storage and retrieval
- **Emoji Support:** Click emoji panel or use text codes
- **File Sharing:** Share images, documents, and other files

### User Interface
- **Modern Design:** Clean, intuitive Tkinter interface
- **Responsive Layout:** Adapts to window resizing
- **Status Indicators:** Connection and room status
- **Message Display:** Formatted chat with timestamps

## Technical Implementation

### Networking
- **Socket Programming:** TCP sockets for reliable communication
- **Multi-threading:** Separate thread for each client connection
- **Protocol Handling:** Support for both text and JSON protocols

### Data Storage
- **SQLite Database:** Lightweight, file-based database
- **Schema Design:** Normalized tables for users, rooms, and messages
- **Data Persistence:** Automatic saving of messages and user data

### Security
- **Password Hashing:** PBKDF2 with salt for secure password storage
- **Input Validation:** Basic validation for user inputs
- **Error Handling:** Graceful handling of network and database errors

## Advanced Features Explained

### Emoji System
```python
emoji_map = {
    ":smile:": "😊", ":laugh:": "😂", ":heart:": "❤️",
    ":thumbs_up:": "👍", ":party:": "🎉", ":rocket:": "🚀"
}
```

### Message History
- Messages stored in SQLite with timestamps
- Automatic cleanup of old messages
- Room-based message isolation

### File Sharing
- Support for multiple file types
- File size validation
- Base64 encoding for transmission

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Kill process using the port
   lsof -ti:5555 | xargs kill -9
   ```

2. **Connection refused:**
   - Ensure server is running
   - Check firewall settings
   - Verify IP address and port

3. **Database locked:**
   - Close all database connections
   - Restart the application

4. **GUI not responding:**
   - Check for Python Tkinter installation
   - Restart the application

### Testing

1. **Local Testing:**
   ```bash
   # Terminal 1 - Start server
   python chat_server.py

   # Terminal 2 - Start basic client
   python basic_client.py localhost

   # Terminal 3 - Start GUI client
   python gui_chat_app.py
   ```

2. **Network Testing:**
   - Use actual IP address instead of localhost
   - Ensure firewall allows the port
   - Test from different machines

## Future Enhancements

- **Encryption:** End-to-end message encryption
- **Push Notifications:** Desktop notifications for new messages
- **Voice/Video:** Audio and video calling features
- **Message Reactions:** Like/emoji reactions to messages
- **Search:** Message search functionality
- **Themes:** Dark/light theme support
- **Mobile App:** Cross-platform mobile application

## Learning Outcomes

This project demonstrates:

- **Network Programming:** Socket programming and client-server architecture
- **GUI Development:** Tkinter for desktop applications
- **Database Design:** SQLite for data persistence
- **Security Practices:** Password hashing and validation
- **Multi-threading:** Concurrent client handling
- **Protocol Design:** Custom communication protocols
- **User Experience:** Intuitive interface design

## License

This project is part of the Oasis Infobyte Summer Internship Program and is intended for educational purposes.

---

**Created by:** Oasis Infobyte Summer Internship Program
**Technologies:** Python, Tkinter, SQLite, Socket Programming
**Version:** 1.0.0
