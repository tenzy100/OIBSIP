"""
BMI Calculator - PyQt5 GUI Version
Features: User profiles, historical data, trend analysis, and visualization
"""

import sys
import json
import os
from datetime import datetime

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                                 QTextEdit, QRadioButton, QGroupBox, QMessageBox,
                                 QTableWidget, QTableWidgetItem, QHeaderView)
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont, QColor
except ImportError:
    print("ERROR: PyQt5 is not installed!")
    print("Please install it using: pip install PyQt5")
    sys.exit(1)

try:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not installed. Chart features will be disabled.")
    print("Install using: pip install matplotlib")

class BMICalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_file = "bmi_data.json"
        self.user_data = {}
        self.load_data()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('BMI Calculator Pro')
        self.setGeometry(100, 100, 800, 700)
        
        # Center window on screen
        self.center_window()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Set style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 10px;
                background-color: #f8f9fa;
                font-size: 10px;
            }
            QLabel {
                font-size: 11px;
            }
        """)
        
        # Title
        title = QLabel('BMI Calculator Pro')
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title)
        
        # Input section
        input_group = QGroupBox('Personal Information')
        input_layout = QVBoxLayout()
        
        # Name
        name_layout = QHBoxLayout()
        name_label = QLabel('Name:')
        name_label.setFixedWidth(100)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Enter your name')
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        input_layout.addLayout(name_layout)
        
        # Weight
        weight_layout = QHBoxLayout()
        weight_label = QLabel('Weight:')
        weight_label.setFixedWidth(100)
        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText('Enter weight')
        weight_layout.addWidget(weight_label)
        weight_layout.addWidget(self.weight_input)
        input_layout.addLayout(weight_layout)
        
        # Height
        height_layout = QHBoxLayout()
        height_label = QLabel('Height:')
        height_label.setFixedWidth(100)
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText('Enter height')
        height_layout.addWidget(height_label)
        height_layout.addWidget(self.height_input)
        input_layout.addLayout(height_layout)
        
        # Unit selection
        unit_layout = QHBoxLayout()
        unit_label = QLabel('Units:')
        unit_label.setFixedWidth(100)
        self.metric_radio = QRadioButton('Metric (kg, cm)')
        self.imperial_radio = QRadioButton('Imperial (lbs, inches)')
        self.metric_radio.setChecked(True)
        unit_layout.addWidget(unit_label)
        unit_layout.addWidget(self.metric_radio)
        unit_layout.addWidget(self.imperial_radio)
        unit_layout.addStretch()
        input_layout.addLayout(unit_layout)
        
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        calc_button = QPushButton('Calculate BMI')
        calc_button.clicked.connect(self.calculate_bmi)
        button_layout.addWidget(calc_button)
        
        history_button = QPushButton('View History')
        history_button.clicked.connect(self.show_history)
        button_layout.addWidget(history_button)
        
        clear_button = QPushButton('Clear')
        clear_button.clicked.connect(self.clear_inputs)
        button_layout.addWidget(clear_button)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Results section
        result_group = QGroupBox('Results')
        result_layout = QVBoxLayout()
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(150)
        result_layout.addWidget(self.result_text)
        
        result_group.setLayout(result_layout)
        main_layout.addWidget(result_group)
        
        # Chart section (if matplotlib available)
        if MATPLOTLIB_AVAILABLE:
            self.chart_group = QGroupBox('BMI Trend')
            self.chart_layout = QVBoxLayout()
            self.chart_group.setLayout(self.chart_layout)
            main_layout.addWidget(self.chart_group)
        
        main_layout.addStretch()
        
    def center_window(self):
        """Center the window on screen"""
        screen = QApplication.desktop().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
        
    def load_data(self):
        """Load user data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.user_data = json.load(f)
            except:
                self.user_data = {}
        else:
            self.user_data = {}
    
    def save_data(self):
        """Save user data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.user_data, f, indent=4)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data: {str(e)}")
            return False
    
    def validate_inputs(self):
        """Validate user inputs"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter your name")
            return None
        
        try:
            weight = float(self.weight_input.text())
            height = float(self.height_input.text())
            
            if self.metric_radio.isChecked():
                if not (20 <= weight <= 300):
                    QMessageBox.warning(self, "Error", "Weight must be between 20-300 kg")
                    return None
                if not (50 <= height <= 250):
                    QMessageBox.warning(self, "Error", "Height must be between 50-250 cm")
                    return None
            else:  # imperial
                if not (44 <= weight <= 660):
                    QMessageBox.warning(self, "Error", "Weight must be between 44-660 lbs")
                    return None
                if not (20 <= height <= 100):
                    QMessageBox.warning(self, "Error", "Height must be between 20-100 inches")
                    return None
            
            return name, weight, height
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter valid numeric values")
            return None
    
    def calculate_bmi(self):
        """Calculate BMI and display results"""
        validation = self.validate_inputs()
        if not validation:
            return
        
        name, weight, height = validation
        
        # Convert to metric if needed
        if self.imperial_radio.isChecked():
            weight = weight * 0.453592  # lbs to kg
            height = height * 2.54  # inches to cm
        
        # Convert height to meters
        height_m = height / 100
        
        # Calculate BMI
        bmi = weight / (height_m ** 2)
        
        # Classify BMI
        category, color = self.classify_bmi(bmi)
        
        # Store data
        self.store_bmi_record(name, weight, height, bmi, category)
        
        # Display results
        self.display_results(name, bmi, category, color)
        
        # Update chart
        if MATPLOTLIB_AVAILABLE:
            self.update_chart(name)
    
    def classify_bmi(self, bmi):
        """Classify BMI into health categories"""
        if bmi < 18.5:
            return "Underweight", "#3498db"
        elif 18.5 <= bmi < 25:
            return "Normal weight", "#2ecc71"
        elif 25 <= bmi < 30:
            return "Overweight", "#f39c12"
        elif 30 <= bmi < 35:
            return "Obese (Class I)", "#e67e22"
        elif 35 <= bmi < 40:
            return "Obese (Class II)", "#e74c3c"
        else:
            return "Obese (Class III)", "#c0392b"
    
    def store_bmi_record(self, name, weight, height, bmi, category):
        """Store BMI record for user"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if name not in self.user_data:
            self.user_data[name] = []
        
        record = {
            "date": timestamp,
            "weight": round(weight, 2),
            "height": round(height, 2),
            "bmi": round(bmi, 2),
            "category": category
        }
        
        self.user_data[name].append(record)
        self.save_data()
    
    def display_results(self, name, bmi, category, color):
        """Display BMI results"""
        result = f"<h3 style='color: #2c3e50;'>BMI CALCULATION RESULTS FOR {name.upper()}</h3>"
        result += "<hr>"
        result += f"<p><b>Your BMI:</b> <span style='font-size: 16px; color: {color};'>{bmi:.2f}</span></p>"
        result += f"<p><b>Category:</b> <span style='color: {color}; font-weight: bold;'>{category}</span></p>"
        result += "<hr>"
        result += "<p><b>Health Recommendations:</b></p><ul>"
        
        if bmi < 18.5:
            result += "<li>Consider consulting a healthcare provider</li>"
            result += "<li>Focus on balanced nutrition and healthy weight gain</li>"
        elif 18.5 <= bmi < 25:
            result += "<li>Maintain your current healthy lifestyle</li>"
            result += "<li>Continue balanced diet and regular exercise</li>"
        elif 25 <= bmi < 30:
            result += "<li>Consider lifestyle modifications</li>"
            result += "<li>Increase physical activity and monitor diet</li>"
        else:
            result += "<li>Consult with a healthcare professional</li>"
            result += "<li>Develop a comprehensive weight management plan</li>"
        
        result += "</ul>"
        self.result_text.setHtml(result)
    
    def update_chart(self, name):
        """Update BMI trend chart for user"""
        # Clear previous chart
        for i in reversed(range(self.chart_layout.count())): 
            self.chart_layout.itemAt(i).widget().setParent(None)
        
        if name not in self.user_data or len(self.user_data[name]) < 2:
            label = QLabel("Record more BMI entries to view trend analysis")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("padding: 20px; font-size: 12px;")
            self.chart_layout.addWidget(label)
            return
        
        # Prepare data
        records = self.user_data[name]
        bmis = [r["bmi"] for r in records]
        
        # Create figure
        fig = Figure(figsize=(7, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Plot BMI trend
        ax.plot(range(len(bmis)), bmis, marker='o', linewidth=2, markersize=6, color='#3498db')
        ax.set_xlabel('Record Number', fontsize=10)
        ax.set_ylabel('BMI', fontsize=10)
        ax.set_title(f'BMI Trend for {name}', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add category zones
        ax.axhspan(0, 18.5, alpha=0.1, color='blue', label='Underweight')
        ax.axhspan(18.5, 25, alpha=0.1, color='green', label='Normal')
        ax.axhspan(25, 30, alpha=0.1, color='yellow', label='Overweight')
        ax.axhspan(30, 50, alpha=0.1, color='red', label='Obese')
        
        ax.legend(loc='upper right', fontsize=8)
        fig.tight_layout()
        
        # Display chart
        canvas = FigureCanvasQTAgg(fig)
        self.chart_layout.addWidget(canvas)
    
    def show_history(self):
        """Show user history in a new window"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter a name to view history")
            return
        
        if name not in self.user_data or not self.user_data[name]:
            QMessageBox.information(self, "Info", f"No history found for {name}")
            return
        
        # Create history dialog
        history_dialog = QWidget()
        history_dialog.setWindowTitle(f"History - {name}")
        history_dialog.setGeometry(200, 200, 700, 400)
        
        layout = QVBoxLayout()
        
        # Create table
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Date", "Weight (kg)", "Height (cm)", "BMI", "Category"])
        
        records = self.user_data[name]
        table.setRowCount(len(records))
        
        for i, record in enumerate(reversed(records)):
            table.setItem(i, 0, QTableWidgetItem(record["date"]))
            table.setItem(i, 1, QTableWidgetItem(str(record["weight"])))
            table.setItem(i, 2, QTableWidgetItem(str(record["height"])))
            table.setItem(i, 3, QTableWidgetItem(str(record["bmi"])))
            table.setItem(i, 4, QTableWidgetItem(record["category"]))
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table)
        
        # Statistics
        bmis = [r["bmi"] for r in records]
        avg_bmi = sum(bmis) / len(bmis)
        min_bmi = min(bmis)
        max_bmi = max(bmis)
        
        stats_label = QLabel(
            f"<b>Statistics:</b> Average BMI: {avg_bmi:.2f} | "
            f"Min: {min_bmi:.2f} | Max: {max_bmi:.2f} | Total Records: {len(bmis)}"
        )
        stats_label.setStyleSheet("padding: 10px; font-size: 11px;")
        layout.addWidget(stats_label)
        
        history_dialog.setLayout(layout)
        history_dialog.show()
        
        # Keep reference to prevent garbage collection
        self.history_window = history_dialog
    
    def clear_inputs(self):
        """Clear all input fields"""
        self.name_input.clear()
        self.weight_input.clear()
        self.height_input.clear()
        self.result_text.clear()
        
        if MATPLOTLIB_AVAILABLE:
            for i in reversed(range(self.chart_layout.count())): 
                self.chart_layout.itemAt(i).widget().setParent(None)

def main():
    app = QApplication(sys.argv)
    calculator = BMICalculator()
    calculator.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()