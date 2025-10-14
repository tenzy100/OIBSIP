# OASIS Infobyte Internship Projects

This repository contains multiple projects completed during the OASIS Infobyte internship program.

## Projects

### 1. BMI Calculator
A Body Mass Index (BMI) calculator with both GUI and CLI interfaces. Features include:
- Weight and height input validation
- BMI category classification with personalized advice
- History tracking of BMI calculations
- Visual representation of BMI trends over time
- User-friendly graphical interface

### 2. Chat Application
A versatile chat application with multiple implementations:
- Basic client-server architecture
- GUI-based chat interface
- Web-based chat application
- Features:
  - User authentication
  - Real-time messaging
  - Multiple client support
  - Database storage for messages

### 3. Random Password Generator
A tool for generating secure passwords with:
- Customizable password length
- GUI interface for easy interaction
- Various character type options

## Technologies Used
- Python
- Tkinter (for GUI applications)
- Flask (for web applications)
- SQLite (for database management)
- Matplotlib (for data visualization)

## Project Structure
```
.
├── bmi_calculator/
│   ├── bmi_cli.py
│   ├── bmi_gui.py
│   ├── bmi_history.csv
│   └── main.py
├── chat_app/
│   ├── basic_client.py
│   ├── basic_server.py
│   ├── chat_server.py
│   ├── gui_chat_app.py
│   ├── web_chat_app.py
│   └── templates/
│       ├── chat.html
│       ├── login.html
│       └── register.html
└── random_password_generator/
    ├── password_generator.py
    └── password_gui.py
```

## Getting Started

### Prerequisites
- Python 3.x
- Required Python packages:
  ```
  tkinter
  matplotlib
  flask
  ```

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/tenzy100/OIBSIP.git
   cd OIBSIP
   ```

2. Install required dependencies:
   ```bash
   pip install -r chat_app/requirements.txt
   ```

### Running the Applications

#### BMI Calculator
```bash
cd bmi_calculator
python bmi_gui.py  # For GUI version
python bmi_cli.py  # For CLI version
```

#### Chat Application
```bash
cd chat_app
python chat_server.py  # Start the server first
python gui_chat_app.py # Start the GUI client
# OR
python web_chat_app.py # Start the web version
```

#### Password Generator
```bash
cd random_password_generator
python password_gui.py
```

## Author
- [@tenzy100](https://github.com/tenzy100)

## License
This project is part of the OASIS Infobyte internship program.