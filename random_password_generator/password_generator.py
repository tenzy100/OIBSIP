import random
import string

def generate_password(length, use_letters=True, use_numbers=True, use_symbols=True):
    characters = ''
    if use_letters:
        characters += string.ascii_letters  # a-zA-Z
    if use_numbers:
        characters += string.digits         # 0-9
    if use_symbols:
        characters += string.punctuation    # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    
    if not characters:
        return "Error: No character set selected!"
    
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

# User Input
try:
    length = int(input("Enter password length: "))
    use_letters = input("Include letters? (y/n): ").lower() == 'y'
    use_numbers = input("Include numbers? (y/n): ").lower() == 'y'
    use_symbols = input("Include symbols? (y/n): ").lower() == 'y'

    password = generate_password(length, use_letters, use_numbers, use_symbols)
    print(f"Generated Password: {password}")
except ValueError:
    print("Invalid input! Please enter a number for password length.")
