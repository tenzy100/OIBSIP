import tkinter as tk
from tkinter import messagebox
import random
import string
import pyperclip

def generate_password():
    try:
        length = int(length_entry.get())
        if length <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a positive number for length.")
        return

    characters = ''
    if letters_var.get():
        characters += string.ascii_letters
    if numbers_var.get():
        characters += string.digits
    if symbols_var.get():
        characters += string.punctuation

    if not characters:
        messagebox.showerror("Error", "Select at least one character type!")
        return

    password = ''.join(random.choice(characters) for _ in range(length))
    password_entry.delete(0, tk.END)
    password_entry.insert(0, password)

def copy_to_clipboard():
    pyperclip.copy(password_entry.get())
    messagebox.showinfo("Copied", "Password copied to clipboard!")

# GUI Setup
root = tk.Tk()
root.title("Random Password Generator")

tk.Label(root, text="Password Length:").grid(row=0, column=0, padx=10, pady=10)
length_entry = tk.Entry(root)
length_entry.grid(row=0, column=1, padx=10, pady=10)

letters_var = tk.BooleanVar(value=True)
numbers_var = tk.BooleanVar(value=True)
symbols_var = tk.BooleanVar(value=True)

tk.Checkbutton(root, text="Letters", variable=letters_var).grid(row=1, column=0, sticky='w')
tk.Checkbutton(root, text="Numbers", variable=numbers_var).grid(row=1, column=1, sticky='w')
tk.Checkbutton(root, text="Symbols", variable=symbols_var).grid(row=1, column=2, sticky='w')

tk.Button(root, text="Generate Password", command=generate_password).grid(row=2, column=0, columnspan=3, pady=10)

password_entry = tk.Entry(root, width=30)
password_entry.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard).grid(row=3, column=2, padx=10, pady=10)

root.mainloop()
