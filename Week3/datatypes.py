# data_types_security.py
# Demonstrating data types with cybersecurity examples

print("=== Integer Examples ===")
ssh_port = 22
rdp_port = 3389
failed_attempts = 5

print(f"SSH runs on port: {ssh_port}")
print(f"RDP runs on port: {rdp_port}")
print(f"Failed login attempts: {failed_attempts}")

# Integer operations
total_ports = ssh_port + rdp_port
print(f"Sum of ports: {total_ports}")

print("\n=== Float Examples ===")
cvss_score = 7.5
packet_loss = 0.023
response_time = 0.125

print(f"CVSS Score: {cvss_score}")
print(f"Packet loss: {packet_loss * 100}%")
print(f"Response time: {response_time} seconds")

# Float precision issues
a = 0.1 + 0.2
print(f"\n0.1 + 0.2 = {a}")  # Not exactly 0.3!
print(f"Is it 0.3? {a == 0.3}")  # False!

print("\n=== String Examples ===")
ip_address = "192.168.1.100"
username = "admin"
log_entry = "Failed authentication from unknown source"

print(f"Target IP: {ip_address}")
print(f"Username: {username}")
print(f"Log: {log_entry}")

# String operations
full_alert = "[ALERT] " + log_entry + " - IP: " + ip_address
print(f"\nFormatted alert: {full_alert}")

# String methods
print(f"Username uppercase: {username.upper()}")
print(f"Log starts with 'Failed': {log_entry.startswith('Failed')}")

print("\n=== Boolean Examples ===")
is_admin = True
account_locked = False
port_open = True

print(f"Admin status: {is_admin}")
print(f"Account locked: {account_locked}")
print(f"Port 22 open: {port_open}")

# Boolean logic
if is_admin and not account_locked:
    print("Access granted")
else:
    print("Access denied")