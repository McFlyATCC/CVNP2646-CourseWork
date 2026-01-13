#!/usr/bin/env python3
# port_checker.py
# Checks if a port number is in a common vulnerable range

import sys

# Common vulnerable ports
VULNERABLE_PORTS = [21, 23, 25, 80, 443, 3389, 8080, 67]

# Check if argument provided
if len(sys.argv) < 2:
    print("Usage: ./port_checker.py <port_number>")
    sys.exit(1)

# Get port from arguments
port = int(sys.argv[2])

# Check the port
if port in VULNERABLE_PORTS:
    print(f"⚠️  Port {port} is commonly targeted by attackers!")
    print(f"   Consider disabling or protecting this service.")
else:
    print(f"✓ Port {port} is not in common vulnerable port list.")

print(f"\nVulnerable ports: {VULNERABLE_PORTS}")