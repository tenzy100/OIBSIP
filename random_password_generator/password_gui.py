"""
Advanced Random Password Generator - PyQt5 Version
Features: Customizable generation, strength meter, history, clipboard integration
"""

import sys
import random
import string
import json
import os
from datetime import datetime

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                                 QCheckBox, QSpinBox, QTextEdit, QGroupBox, 
                                 QMessageBox, QProgressBar, QTableWidget, 
                                 QTableWidgetItem, QHeaderView, QSlider, QComboBox)
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QFont, QColor, QClipboard, QIcon
except ImportError:
    print("ERROR: PyQt5 is not installed!")
    print("Please install it using: pip install PyQt5")
    sys.exit(1)

class PasswordGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.history_file = "password_history.json"
        self.password_history = []
        self.load_history()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('Advanced Password Generator Pro')
        self.setGeometry(100, 100, 900, 750)
        self.center_window()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Apply stylesheet
        self.apply_stylesheet()
        
        # Title
        title = QLabel('🔐 Advanced Password Generator Pro')
        title.setFont(QFont('Arial', 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin: 15px; padding: 10px;")
        main_layout.addWidget(title)
        
        # Password Display Section
        display_group = QGroupBox('Generated Password')
        display_layout = QVBoxLayout()
        
        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setPlaceholderText('Your generated password will appear here...')
        self.password_display.setFont(QFont('Courier New', 14, QFont.Bold))
        self.password_display.setAlignment(Qt.AlignCenter)
        self.password_display.setStyleSheet("""
            QLineEdit {
                padding: 15px;
                border: 3px solid #3498db;
                border-radius: 8px;
                background-color: #ecf0f1;
                color: #2c3e50;
            }
        """)
        display_layout.addWidget(self.password_display)
        
        # Password strength indicator
        strength_layout = QHBoxLayout()
        strength_label = QLabel('Password Strength:')
        strength_label.setFont(QFont('Arial', 10, QFont.Bold))
        self.strength_bar = QProgressBar()
        self.strength_bar.setMaximum(100)
        self.strength_bar.setValue(0)
        self.strength_bar.setTextVisible(True)
        self.strength_bar.setFormat('%p% - %v')
        strength_layout.addWidget(strength_label)
        strength_layout.addWidget(self.strength_bar)
        display_layout.addLayout(strength_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton('🎲 Generate Password')
        self.generate_btn.clicked.connect(self.generate_password)
        self.generate_btn.setMinimumHeight(45)
        
        self.copy_btn = QPushButton('📋 Copy to Clipboard')
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.copy_btn.setEnabled(False)
        self.copy_btn.setMinimumHeight(45)
        
        self.save_btn = QPushButton('💾 Save Password')
        self.save_btn.clicked.connect(self.save_password)
        self.save_btn.setEnabled(False)
        self.save_btn.setMinimumHeight(45)
        
        button_layout.addWidget(self.generate_btn)
        button_layout.addWidget(self.copy_btn)
        button_layout.addWidget(self.save_btn)
        display_layout.addLayout(button_layout)
        
        display_group.setLayout(display_layout)
        main_layout.addWidget(display_group)
        
        # Configuration Section
        config_layout = QHBoxLayout()
        
        # Left Column - Basic Settings
        basic_group = QGroupBox('Basic Settings')
        basic_layout = QVBoxLayout()
        
        # Password Length
        length_layout = QHBoxLayout()
        length_label = QLabel('Password Length:')
        self.length_spinbox = QSpinBox()
        self.length_spinbox.setMinimum(4)
        self.length_spinbox.setMaximum(128)
        self.length_spinbox.setValue(16)
        self.length_spinbox.setFixedWidth(80)
        self.length_slider = QSlider(Qt.Horizontal)
        self.length_slider.setMinimum(4)
        self.length_slider.setMaximum(128)
        self.length_slider.setValue(16)
        self.length_slider.valueChanged.connect(self.length_spinbox.setValue)
        self.length_spinbox.valueChanged.connect(self.length_slider.setValue)
        length_layout.addWidget(length_label)
        length_layout.addWidget(self.length_spinbox)
        length_layout.addWidget(self.length_slider)
        basic_layout.addLayout(length_layout)
        
        # Number of Passwords
        count_layout = QHBoxLayout()
        count_label = QLabel('Generate Count:')
        self.count_spinbox = QSpinBox()
        self.count_spinbox.setMinimum(1)
        self.count_spinbox.setMaximum(10)
        self.count_spinbox.setValue(1)
        self.count_spinbox.setFixedWidth(80)
        count_layout.addWidget(count_label)
        count_layout.addWidget(self.count_spinbox)
        count_layout.addStretch()
        basic_layout.addLayout(count_layout)
        
        # Character Type Checkboxes
        self.uppercase_check = QCheckBox('Uppercase Letters (A-Z)')
        self.uppercase_check.setChecked(True)
        basic_layout.addWidget(self.uppercase_check)
        
        self.lowercase_check = QCheckBox('Lowercase Letters (a-z)')
        self.lowercase_check.setChecked(True)
        basic_layout.addWidget(self.lowercase_check)
        
        self.numbers_check = QCheckBox('Numbers (0-9)')
        self.numbers_check.setChecked(True)
        basic_layout.addWidget(self.numbers_check)
        
        self.symbols_check = QCheckBox('Symbols (!@#$%^&*)')
        self.symbols_check.setChecked(True)
        basic_layout.addWidget(self.symbols_check)
        
        basic_group.setLayout(basic_layout)
        config_layout.addWidget(basic_group)
        
        # Right Column - Advanced Settings
        advanced_group = QGroupBox('Advanced Settings')
        advanced_layout = QVBoxLayout()
        
        # Security Rules Label
        security_label = QLabel('Security Rules:')
        security_label.setFont(QFont('Arial', 10, QFont.Bold))
        security_label.setStyleSheet("color: #2c3e50; margin-top: 5px;")
        advanced_layout.addWidget(security_label)
        
        self.no_ambiguous_check = QCheckBox('Exclude Ambiguous Characters (O0Il1)')
        self.no_ambiguous_check.setChecked(False)
        advanced_layout.addWidget(self.no_ambiguous_check)
        
        self.no_repeating_check = QCheckBox('No Consecutive Repeating Characters')
        self.no_repeating_check.setChecked(False)
        advanced_layout.addWidget(self.no_repeating_check)
        
        self.must_include_all_check = QCheckBox('Must Include All Selected Types')
        self.must_include_all_check.setChecked(True)
        advanced_layout.addWidget(self.must_include_all_check)
        
        # Custom Characters
        custom_layout = QVBoxLayout()
        custom_label = QLabel('Custom Characters to Include:')
        custom_label.setStyleSheet("color: #2c3e50; font-weight: bold; margin-top: 10px;")
        self.custom_include_input = QLineEdit()
        self.custom_include_input.setPlaceholderText('e.g., @#$%')
        custom_layout.addWidget(custom_label)
        custom_layout.addWidget(self.custom_include_input)
        advanced_layout.addLayout(custom_layout)
        
        # Exclude Characters
        exclude_layout = QVBoxLayout()
        exclude_label = QLabel('Characters to Exclude:')
        exclude_label.setStyleSheet("color: #2c3e50; font-weight: bold; margin-top: 5px;")
        self.exclude_input = QLineEdit()
        self.exclude_input.setPlaceholderText('e.g., O0Il1')
        exclude_layout.addWidget(exclude_label)
        exclude_layout.addWidget(self.exclude_input)
        advanced_layout.addLayout(exclude_layout)
        
        # Password Pattern
        pattern_layout = QVBoxLayout()
        pattern_label = QLabel('Password Pattern (Optional):')
        pattern_label.setStyleSheet("color: #2c3e50; font-weight: bold; margin-top: 5px;")
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems([
            'Random',
            'Starts with Letter',
            'Ends with Number',
            'Alternating Letters-Numbers',
            'Custom Pattern'
        ])
        pattern_layout.addWidget(pattern_label)
        pattern_layout.addWidget(self.pattern_combo)
        advanced_layout.addLayout(pattern_layout)
        
        advanced_group.setLayout(advanced_layout)
        config_layout.addWidget(advanced_group)
        
        main_layout.addLayout(config_layout)
        
        # History Section
        history_group = QGroupBox('Password History')
        history_layout = QVBoxLayout()
        
        # History controls
        history_controls = QHBoxLayout()
        view_history_btn = QPushButton('📜 View Full History')
        view_history_btn.clicked.connect(self.show_full_history)
        clear_history_btn = QPushButton('🗑️ Clear History')
        clear_history_btn.clicked.connect(self.clear_history)
        history_controls.addWidget(view_history_btn)
        history_controls.addWidget(clear_history_btn)
        history_controls.addStretch()
        history_layout.addLayout(history_controls)
        
        # Recent passwords display
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setMaximumHeight(100)
        self.history_text.setPlaceholderText('Recent passwords will appear here...')
        history_layout.addWidget(self.history_text)
        
        history_group.setLayout(history_layout)
        main_layout.addWidget(history_group)
        
        # Status bar
        self.statusBar().showMessage('Ready to generate secure passwords!')
        
        # Update history display
        self.update_history_display()
        
    def apply_stylesheet(self):
        """Apply custom stylesheet to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 12px;
                padding: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 11px;
                background-color: white;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 11px;
                color: #2c3e50;
                background-color: white;
            }
            QCheckBox {
                font-size: 11px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
                background-color: #f8f9fa;
                font-size: 10px;
                font-family: 'Courier New';
            }
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 11px;
                color: #2c3e50;
                background-color: white;
            }
            QSlider::groove:horizontal {
                border: 1px solid #bdc3c7;
                height: 8px;
                background: #ecf0f1;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                border: 1px solid #2980b9;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)
        
    def center_window(self):
        """Center the window on screen"""
        screen = QApplication.desktop().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
        
    def load_history(self):
        """Load password history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    self.password_history = json.load(f)
            except:
                self.password_history = []
        else:
            self.password_history = []
    
    def save_history(self):
        """Save password history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.password_history, f, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to save history: {str(e)}")
    
    def generate_password(self):
        """Generate password based on user settings"""
        try:
            # Validate at least one character type is selected
            if not any([self.uppercase_check.isChecked(), 
                       self.lowercase_check.isChecked(),
                       self.numbers_check.isChecked(), 
                       self.symbols_check.isChecked()]):
                QMessageBox.warning(self, "Error", "Please select at least one character type!")
                return
            
            # Get settings
            length = self.length_spinbox.value()
            count = self.count_spinbox.value()
            
            # Build character set
            char_set = self.build_character_set()
            
            if not char_set:
                QMessageBox.warning(self, "Error", "No valid characters available for password generation!")
                return
            
            # Generate password(s)
            generated_passwords = []
            for _ in range(count):
                password = self.create_password(char_set, length)
                generated_passwords.append(password)
            
            # Display password(s)
            if count == 1:
                self.password_display.setText(generated_passwords[0])
                self.current_password = generated_passwords[0]
            else:
                display_text = '\n'.join([f"{i+1}. {pwd}" for i, pwd in enumerate(generated_passwords)])
                self.password_display.setText(display_text)
                self.current_password = generated_passwords[0]
            
            # Calculate and display strength
            strength = self.calculate_strength(self.current_password)
            self.update_strength_meter(strength)
            
            # Enable buttons
            self.copy_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            
            self.statusBar().showMessage(f'✓ Generated {count} password(s) successfully!', 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate password: {str(e)}")
    
    def build_character_set(self):
        """Build character set based on user selections"""
        char_set = ''
        
        if self.uppercase_check.isChecked():
            char_set += string.ascii_uppercase
        if self.lowercase_check.isChecked():
            char_set += string.ascii_lowercase
        if self.numbers_check.isChecked():
            char_set += string.digits
        if self.symbols_check.isChecked():
            char_set += '!@#$%^&*()_+-=[]{}|;:,.<>?'
        
        # Add custom characters
        custom_chars = self.custom_include_input.text()
        if custom_chars:
            char_set += custom_chars
        
        # Remove ambiguous characters if checked
        if self.no_ambiguous_check.isChecked():
            ambiguous = 'O0Il1'
            char_set = ''.join(c for c in char_set if c not in ambiguous)
        
        # Remove excluded characters
        excluded = self.exclude_input.text()
        if excluded:
            char_set = ''.join(c for c in char_set if c not in excluded)
        
        return char_set
    
    def create_password(self, char_set, length):
        """Create a single password"""
        password = []
        
        # Ensure all required types are included if checked
        if self.must_include_all_check.isChecked():
            if self.uppercase_check.isChecked():
                password.append(random.choice(string.ascii_uppercase))
            if self.lowercase_check.isChecked():
                password.append(random.choice(string.ascii_lowercase))
            if self.numbers_check.isChecked():
                password.append(random.choice(string.digits))
            if self.symbols_check.isChecked():
                password.append(random.choice('!@#$%^&*()_+-=[]{}|;:,.<>?'))
        
        # Fill the rest randomly
        while len(password) < length:
            char = random.choice(char_set)
            
            # Check for repeating characters
            if self.no_repeating_check.isChecked() and password and char == password[-1]:
                continue
            
            password.append(char)
        
        # Shuffle the password
        random.shuffle(password)
        
        # Apply pattern if selected
        pattern = self.pattern_combo.currentText()
        if pattern == 'Starts with Letter':
            if password[0].isdigit():
                # Find first letter and swap
                for i, c in enumerate(password):
                    if c.isalpha():
                        password[0], password[i] = password[i], password[0]
                        break
        elif pattern == 'Ends with Number':
            if not password[-1].isdigit():
                # Find first number and swap
                for i, c in enumerate(password):
                    if c.isdigit():
                        password[-1], password[i] = password[i], password[-1]
                        break
        
        return ''.join(password)
    
    def calculate_strength(self, password):
        """Calculate password strength (0-100)"""
        if not password:
            return 0
        
        strength = 0
        
        # Length factor (0-30 points)
        length = len(password)
        if length >= 16:
            strength += 30
        elif length >= 12:
            strength += 25
        elif length >= 8:
            strength += 20
        else:
            strength += length * 2
        
        # Character variety (0-40 points)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        
        variety_count = sum([has_upper, has_lower, has_digit, has_symbol])
        strength += variety_count * 10
        
        # Uniqueness (0-20 points)
        unique_chars = len(set(password))
        uniqueness_ratio = unique_chars / len(password)
        strength += int(uniqueness_ratio * 20)
        
        # No repeating patterns (0-10 points)
        has_repeating = any(password[i] == password[i+1] for i in range(len(password)-1))
        if not has_repeating:
            strength += 10
        
        return min(strength, 100)
    
    def update_strength_meter(self, strength):
        """Update the strength meter display"""
        self.strength_bar.setValue(strength)
        
        # Update color based on strength
        if strength < 40:
            color = '#e74c3c'  # Red - Weak
            text = 'Weak'
        elif strength < 70:
            color = '#f39c12'  # Orange - Moderate
            text = 'Moderate'
        else:
            color = '#2ecc71'  # Green - Strong
            text = 'Strong'
        
        self.strength_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        self.strength_bar.setFormat(f'{strength}% - {text}')
    
    def copy_to_clipboard(self):
        """Copy password to clipboard"""
        password = self.password_display.text()
        if password:
            clipboard = QApplication.clipboard()
            clipboard.setText(password)
            self.statusBar().showMessage('✓ Password copied to clipboard!', 3000)
            
            # Show temporary notification
            QMessageBox.information(self, "Copied", 
                                   "Password has been copied to clipboard!\n\n"
                                   "⚠️ Remember to paste it somewhere safe.")
    
    def save_password(self):
        """Save password to history"""
        password = self.current_password if hasattr(self, 'current_password') else self.password_display.text()
        
        if password:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            strength = self.calculate_strength(password)
            
            record = {
                "password": password,
                "timestamp": timestamp,
                "length": len(password),
                "strength": strength
            }
            
            self.password_history.insert(0, record)
            
            # Keep only last 50 passwords
            if len(self.password_history) > 50:
                self.password_history = self.password_history[:50]
            
            self.save_history()
            self.update_history_display()
            
            self.statusBar().showMessage('✓ Password saved to history!', 3000)
    
    def update_history_display(self):
        """Update the history text display"""
        if not self.password_history:
            self.history_text.setPlainText("No passwords in history yet.")
            return
        
        # Show last 3 passwords
        recent = self.password_history[:3]
        text = ""
        for i, record in enumerate(recent, 1):
            text += f"{i}. {record['password']} (Strength: {record['strength']}%, {record['timestamp']})\n"
        
        self.history_text.setPlainText(text.strip())
    
    def show_full_history(self):
        """Show full password history in a new window"""
        if not self.password_history:
            QMessageBox.information(self, "History", "No passwords in history yet.")
            return
        
        # Create history dialog
        history_dialog = QWidget()
        history_dialog.setWindowTitle("Password History")
        history_dialog.setGeometry(150, 150, 800, 500)
        
        layout = QVBoxLayout()
        
        # Create table
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Password", "Length", "Strength", "Date & Time"])
        
        table.setRowCount(len(self.password_history))
        
        for i, record in enumerate(self.password_history):
            table.setItem(i, 0, QTableWidgetItem(record["password"]))
            table.setItem(i, 1, QTableWidgetItem(str(record["length"])))
            table.setItem(i, 2, QTableWidgetItem(f"{record['strength']}%"))
            table.setItem(i, 3, QTableWidgetItem(record["timestamp"]))
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table)
        
        # Export button
        export_btn = QPushButton('📤 Export History')
        export_btn.clicked.connect(self.export_history)
        layout.addWidget(export_btn)
        
        history_dialog.setLayout(layout)
        history_dialog.show()
        
        # Keep reference
        self.history_window = history_dialog
    
    def export_history(self):
        """Export history to text file"""
        try:
            filename = f"password_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write("PASSWORD HISTORY EXPORT\n")
                f.write("=" * 80 + "\n\n")
                for record in self.password_history:
                    f.write(f"Password: {record['password']}\n")
                    f.write(f"Length: {record['length']}\n")
                    f.write(f"Strength: {record['strength']}%\n")
                    f.write(f"Generated: {record['timestamp']}\n")
                    f.write("-" * 80 + "\n")
            
            QMessageBox.information(self, "Success", f"History exported to {filename}")
            self.statusBar().showMessage(f'✓ History exported to {filename}', 5000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export history: {str(e)}")
    
    def clear_history(self):
        """Clear password history"""
        reply = QMessageBox.question(self, "Clear History", 
                                     "Are you sure you want to clear all password history?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.password_history = []
            self.save_history()
            self.update_history_display()
            self.statusBar().showMessage('✓ History cleared!', 3000)

def main():
    app = QApplication(sys.argv)
    generator = PasswordGenerator()
    generator.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()