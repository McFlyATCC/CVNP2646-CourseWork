# file_ops.py
# File operation functions for security tools

import json

def load_blocklist(filename):
    """Load IP blocklist from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filename} not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: {filename} is not valid JSON")
        return None

def save_report(filename, data):
    """Save security report to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)