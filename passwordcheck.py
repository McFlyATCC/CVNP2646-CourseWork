#!/usr/bin/env python3
# passwordcheck.py
# Validates password strength based on security requirements

def check_password_strength(password):
    """
    Checks password against security requirements.
    Returns: tuple (is_strong, list_of_issues)
    """
    issues = []

    # Check length
    if len(password) < 8:
        issues.append("❌ Password must be at least 8 characters")

    # Check for lowercase
    if not any(c.islower() for c in password):
        issues.append("❌ Password must contain lowercase letters")

    # Check for uppercase
    if not any(c.isupper() for c in password):
        issues.append("❌ Password must contain uppercase letters")

    # Check for digits
    if not any(c.isdigit() for c in password):
        issues.append("❌ Password must contain numbers")

    # Check for special characters
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        issues.append("❌ Password must contain special characters")

    is_strong = len(issues) == 0
    return is_strong, issues

# Main program
print("=== Password Strength Checker ===\n")
password = input("Enter password to check: ")

is_strong, issues = check_password_strength(password)

if is_strong:
    print("\n✅ Password is STRONG!")
    print("This password meets all security requirements.")
else:
    print("\n⚠️  Password is WEAK!")
    print("Issues found:")
    for issue in issues:
        print(f"  {issue}")