#!/usr/bin/env python3
# hash_generator.py
# Generates cryptographic hashes for file integrity verification

import hashlib
import sys

def generate_hash(filename, algorithm='sha256'):
    """
    Generate hash for a file.
    algorithm: 'md5', 'sha1', 'sha256', 'sha512'
    """
    try:
        # Create hash object
        if algorithm == 'md5':
            hasher = hashlib.md5()
        elif algorithm == 'sha1':
            hasher = hashlib.sha1()
        elif algorithm == 'sha256':
            hasher = hashlib.sha256()
        elif algorithm == 'sha512':
            hasher = hashlib.sha512()
        else:
            print(f"❌ Unknown algorithm: {algorithm}")
            return None

        # Read file and update hash
        with open(filename, 'rb') as f:
            # Read in chunks for large files
            while chunk := f.read(8192):
                hasher.update(chunk)

        return hasher.hexdigest()

    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return None

# Main progrm
if len(sys.argv) < 2:
    print("Usage: ./hash_generator.py <filename> [algorithm]")
    print("Algorithms: md5, sha1, sha256 (default), sha512")
    sys.exit(1)

filename = sys.argv[1]
algorithm = sys.argv[2] if len(sys.argv) > 2 else 'sha256'

print(f"=== File Hash Generator ===")
print(f"File: {filename}")
print(f"Algorithm: {algorithm.upper()}\n")

hash_value = generate_hash(filename, algorithm)

if hash_value:
    print(f"Hash: {hash_value}")
    print(f"\n✅ Hash generated successfully!")