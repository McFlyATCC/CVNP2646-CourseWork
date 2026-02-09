# password_entropy_calculator.py
# Calculates password entropy (bits of randomness)

"""
Password Entropy Calculator

This script estimates how unpredictable a password is by calculating its
Shannon entropy measured in bits. The model assumes each character in the
password is chosen independently and uniformly from a pool of possible
characters (based on the character classes detected in the password).

Entropy formula used:
    H = L * log2(R)

Where:
    - L is the password length (number of characters).
    - R is the size of the effective character pool determined by the
      character classes present (e.g., lowercase = 26, digits = 10, etc.).

DISCLAIMER:
This is a simplified estimate. Real-world password entropy can be lower if:
    - The password uses predictable patterns, common words, or substitutions.
    - Characters are not truly uniformly random.
    - Attackers exploit leaked password frequency data (e.g., dictionaries).
"""

import math  # Provides log base 2 via math.log2

# ---- User Interface Header ----
# Print a title and a short explanation to orient the user before input.
print("=== Password Entropy Calculator ===")
print("Entropy measures password unpredictability in bits\n")

# ---- Input Collection ----
# Prompt the user to enter the password to analyze.
# Note: input() reads raw text from stdin without masking; for real usage,
# consider getpass.getpass() to avoid echoing passwords to the screen.
password = input("Enter password to analyze: ")

# ---- Feature Detection: Character Classes Present ----
# We determine which character classes are present in the password.
# This affects the assumed 'character pool size' R in the entropy formula.

# 1) Lowercase letters: 'a' to 'z'
has_lowercase = any(c.islower() for c in password)

# 2) Uppercase letters: 'A' to 'Z'
has_uppercase = any(c.isupper() for c in password)

# 3) Digits: '0' to '9'
has_digits = any(c.isdigit() for c in password)

# 4) Special characters: a curated set of common symbols
#    NOTE: This is not exhaustive. Different systems may allow more or fewer.
#    If your environment allows a larger set, you can expand this string.
special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"  # Use literal characters in code
has_special = any(c in special_chars for c in password)

# ---- Compute Effective Character Pool Size (R) ----
# Start from zero and add the size contribution for each detected class.
# Typical sizes:
#   - Lowercase: 26 letters
#   - Uppercase: 26 letters
#   - Digits:    10 digits
#   - Special:   we approximate to 32 here (but actual count below is len(special_chars))
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
    # Option A (fixed estimate): add 32, a common rough estimate for symbols.
    # pool_size += 32
    #
    # Option B (exact count based on defined set): use len(special_chars).
    # Choose ONE of the approaches. Below we use the exact count for transparency.
    symbol_count = len(special_chars)
    pool_size += symbol_count
    print(f"✓ Contains special characters (+{symbol_count} pool size)")

# ---- Handle Edge Case: No Recognized Characters ----
# If no valid classes were detected, pool_size remains 0, which would break
# the log2 calculation. We stop here and inform the user.
if pool_size == 0:
    print("❌ Invalid password - no valid characters")
else:
    # ---- Entropy Calculation ----
    # Given password length L and pool size R, entropy H = L * log2(R).
    # This corresponds to the number of bits needed to represent a uniformly
    # random string of length L from an alphabet of size R.

    length = len(password)

    # Use math.log2 for numerical stability and clarity (log base 2).
    entropy = length * math.log2(pool_size)

    # ---- Report Intermediate Values ----
    # Provide transparency: show pool size, length, and final entropy.
    print(f"\nCharacter pool size: {pool_size}")
    print(f"Password length: {length}")
    print(f"Entropy: {entropy:.2f} bits")

    # ---- Interpret Entropy ----
    # Provide a human-friendly strength assessment based on entropy thresholds.
    # Thresholds are heuristic and intended for quick guidance.
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
``
