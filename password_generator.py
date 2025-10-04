import random
import string

def generate_password(length, use_letters=True, use_numbers=True, use_symbols=True):
    char_set = ''
    if use_letters:
        char_set += string.ascii_letters
    if use_numbers:
        char_set += string.digits
    if use_symbols:
        char_set += string.punctuation

    if not char_set:
        return "Error: No character set selected!"

    password = ''.join(random.choice(char_set) for _ in range(length))
    return password

length = int(input("Enter password length: "))
use_letters = input("Include letters? (y/n): ").lower() == 'y'
use_numbers = input("Include numbers? (y/n): ").lower() == 'y'
use_symbols = input("Include symbols? (y/n): ").lower() == 'y'

print("Generated Password:", generate_password(length, use_letters, use_numbers, use_symbols))
