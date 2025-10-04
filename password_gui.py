import tkinter as tk
from tkinter import messagebox
import random
import string
import pyperclip

# Function to generate password
def generate_password():
    try:
        length = int(length_entry.get())
        if length <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Enter a valid positive integer for length")
        return

    char_set = ''
    if letters_var.get():
        char_set += string.ascii_letters
    if numbers_var.get():
        char_set += string.digits
    if symbols_var.get():
        char_set += string.punctuation

    if not char_set:
        messagebox.showerror("Error", "Select at least one character type")
        return

    # Generate password
    password = ''.join(random.choice(char_set) for _ in range(length))
    password_entry.delete(0, tk.END)
    password_entry.insert(0, password)

# Function to copy password
def copy_to_clipboard():
    password = password_entry.get()
    if password:
        pyperclip.copy(password)
        messagebox.showinfo("Copied", "Password copied to clipboard!")
    else:
        messagebox.showwarning("Warning", "No password to copy!")

# GUI Setup
root = tk.Tk()
root.title("Random Password Generator")
root.geometry("500x200")

# Labels and Inputs
tk.Label(root, text="Password Length:").grid(row=0, column=0, padx=10, pady=10)
length_entry = tk.Entry(root)
length_entry.grid(row=0, column=1, padx=10, pady=10)

# Character type options
letters_var = tk.BooleanVar(value=True)
numbers_var = tk.BooleanVar(value=True)
symbols_var = tk.BooleanVar(value=True)

tk.Checkbutton(root, text="Letters", variable=letters_var).grid(row=1, column=0)
tk.Checkbutton(root, text="Numbers", variable=numbers_var).grid(row=1, column=1)
tk.Checkbutton(root, text="Symbols", variable=symbols_var).grid(row=1, column=2)

# Buttons
tk.Button(root, text="Generate Password", command=generate_password).grid(row=2, column=0, columnspan=2, pady=10)
password_entry = tk.Entry(root, width=40)
password_entry.grid(row=2, column=2, padx=10)
tk.Button(root, text="Copy", command=copy_to_clipboard).grid(row=2, column=3, padx=10)

root.mainloop()
