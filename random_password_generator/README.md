# Random Password Generator

A Python-based password generator application that creates secure, customizable passwords with both CLI and GUI interfaces.

## Features

- **Customizable Password Length**: Generate passwords of any desired length
- **Character Type Selection**:
  - Uppercase letters (A-Z)
  - Lowercase letters (a-z)
  - Numbers (0-9)
  - Special characters (!@#$%^&*()_+-=[]{}|;:,.<>?)
- **User-Friendly GUI Interface**: Easy-to-use graphical interface
- **Password Strength Indicator**: Visual feedback on password strength
- **Copy to Clipboard**: One-click copy functionality
- **Input Validation**: Error handling for invalid inputs

## Files

- `password_generator.py`: Core password generation logic
- `password_gui.py`: Graphical user interface implementation

## Requirements

- Python 3.x
- Tkinter (usually comes with Python installation)
- pyperclip (for clipboard functionality)

## Installation

1. Ensure you have Python 3.x installed
2. Install required packages:
   ```bash
   pip install pyperclip
   ```

## Usage

### GUI Version
Run the graphical interface:
```bash
python password_gui.py
```

### Features Guide

1. **Length Selection**: 
   - Use the slider or input field to select password length
   - Recommended length: 12-16 characters for strong passwords

2. **Character Types**:
   - Check/uncheck boxes to include/exclude character types
   - At least one character type must be selected

3. **Generate Password**:
   - Click "Generate Password" button
   - New password will appear in the display field

4. **Copy Password**:
   - Click "Copy to Clipboard" button
   - Password is copied and ready to paste

## Security Features

- Random number generation using Python's `secrets` module for cryptographic operations
- Minimum password length enforcement
- Character type diversity requirements
- Strength indicator based on password complexity

## Best Practices

- Use passwords of at least 12 characters
- Include a mix of all character types
- Generate a new password for each service/account
- Don't store passwords in plain text
- Use a password manager to store generated passwords

## Contributing

If you'd like to contribute:
1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## Author

[@tenzy100](https://github.com/tenzy100)

## License

This project is part of the OASIS Infobyte internship program.

## Acknowledgments

- OASIS Infobyte for the project opportunity
- Python's `secrets` module for secure random generation
- Tkinter for the GUI framework