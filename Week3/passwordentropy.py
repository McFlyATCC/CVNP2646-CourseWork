# password_entropy_calculator.py
# Calculates password entropy (bits of randomness)

import math

print("=== Password Entropy Calculator ===")
print("Entropy measures password unpredictability in bits\n")

password = input("Enter password to analyze: ")

# Determine character pool size
has_lowercase = any(c.islower() for c in password)
has_uppercase = any(c.isupper() for c in password)
has_digits = any(c.isdigit() for c in password)
has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

pool_size = 0
if has_lowercase:
    pool_size += 26
    print("✓ Contains lowercase letters (+26 pool size)")
if has_uppercase:
    pool_size += 26
    print("✓ Contains uppercase letters (+26 pool size)")
if has_digits:
    pool_size += 10
    print("✓ Contains digits (+10 pool size)")
if has_special:
    pool_size += 32
    print("✓ Contains special characters (+32 pool size)")

if pool_size == 0:
    print("❌ Invalid password - no valid characters")
else:
    # Calculate entropy: log2(pool_size ^ length)
    length = len(password)
    entropy = length * math.log2(pool_size)

    print(f"\nCharacter pool size: {pool_size}")
    print(f"Password length: {length}")
    print(f"Entropy: {entropy:.2f} bits")

    # Interpret entropy
    if entropy < 28:
        strength = "VERY WEAK - Crackable instantly"
    elif entropy < 36:
        strength = "WEAK - Crackable in hours"
    elif entropy < 60:
        strength = "MODERATE - Crackable in days/weeks"
    elif entropy < 80:
        strength = "STRONG - Crackable in years"
    else:
        strength = "VERY STRONG - Crackable in centuries"

    print(f"Strength: {strength}")