import tkinter as tk
from tkinter import messagebox
import csv
import os
import matplotlib.pyplot as plt

DATA_FILE = "bmi_history.csv"

def save_bmi_entry(weight, height, bmi, category, advice):
    with open(DATA_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([weight, height, bmi, category, advice])

def load_bmi_history():
    data = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            reader = csv.reader(f)
            data = [row for row in reader]
    return data

def plot_bmi_trend():
    data = load_bmi_history()
    if not data:
        messagebox.showinfo("No Data", "No BMI history found.")
        return
    bmi_values = [float(row[2]) for row in data]
    plt.plot(range(1, len(bmi_values) + 1), bmi_values, marker='o')
    plt.xlabel('Entry Number')
    plt.ylabel('BMI')
    plt.title('BMI Trend Over Time')
    plt.grid(True)
    plt.show()

def calculate_bmi(weight, height):
    return round(float(weight) / (float(height) ** 2), 2)

def bmi_category_and_advice(bmi):
    if bmi < 16:
        return ("Severe Thinness", "Consult a healthcare provider urgently for nutrition support and assessment.")
    elif bmi < 17:
        return ("Moderate Thinness", "You are moderately underweight; improve your nutrition and seek advice.")
    elif bmi < 18.5:
        return ("Mild Thinness", "Consider a balanced diet and regular health monitoring to reach normal BMI.")
    elif bmi < 25:
        return ("Normal", "Maintain your current habits for optimal health—balanced diet, exercise, check-ups.")
    elif bmi < 30:
        return ("Overweight", "Healthy eating and increased physical activity are recommended.")
    elif bmi < 35:
        return ("Obese Class I", "Medical advice and lifestyle changes are recommended for lower health risks.")
    elif bmi < 40:
        return ("Obese Class II", "Seek medical guidance for weight management and to prevent complications.")
    else:
        return ("Obese Class III", "Urgent professional help is strongly advised for health improvement.")

def on_calculate():
    try:
        weight = float(weight_entry.get())
        height = float(height_entry.get())
        if not (20 <= weight <= 300 and 1.0 <= height <= 2.5):
            raise ValueError
        bmi = calculate_bmi(weight, height)
        category, advice = bmi_category_and_advice(bmi)
        result_var.set(f"BMI: {bmi} ({category})")
        advice_var.set(f"Advice: {advice}")
        save_bmi_entry(weight, height, bmi, category, advice)
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter valid weight (20-300 kg) and height (1.0-2.5 m).")

app = tk.Tk()
app.title("BMI Calculator")
app.geometry("400x250")
app.config(bg="lightblue")

tk.Label(app, text="Weight (kg):", bg="lightblue").grid(row=0, column=0, padx=10, pady=5, sticky='e')
tk.Label(app, text="Height (m):", bg="lightblue").grid(row=1, column=0, padx=10, pady=5, sticky='e')

weight_entry = tk.Entry(app)
height_entry = tk.Entry(app)
weight_entry.grid(row=0, column=1, padx=10, pady=5)
height_entry.grid(row=1, column=1, padx=10, pady=5)

result_var = tk.StringVar()
advice_var = tk.StringVar()
tk.Label(app, textvariable=result_var, bg="lightblue", font=("Arial", 11, "bold")).grid(row=2, column=0, columnspan=2, pady=10)
tk.Label(app, textvariable=advice_var, bg="lightblue", wraplength=350, font=("Arial", 10), justify="left").grid(row=3, column=0, columnspan=2, pady=5)

btn_calculate = tk.Button(app, text="Calculate BMI", command=on_calculate, bg="white")
btn_calculate.grid(row=4, column=0, columnspan=2, pady=5)

btn_trend = tk.Button(app, text="Show BMI Trend", command=plot_bmi_trend, bg="white")
btn_trend.grid(row=5, column=0, columnspan=2, pady=5)

app.mainloop()
