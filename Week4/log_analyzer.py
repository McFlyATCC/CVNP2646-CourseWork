# log_analyzer.py
# Read security logs and generate alerts

# First, let's create a sample log file
print("Creating sample security log...")

log_entries = """2024-01-08 10:23:15 - LOGIN SUCCESS - user:admin - ip:192.168.1.50
2024-01-08 10:25:42 - LOGIN FAILED - user:admin - ip:203.0.113.45
2024-01-08 10:26:01 - LOGIN FAILED - user:admin - ip:203.0.113.45
2024-01-08 10:26:18 - LOGIN FAILED - user:admin - ip:203.0.113.45
2024-01-08 10:30:12 - LOGIN SUCCESS - user:jdoe - ip:192.168.1.100
2024-01-08 10:35:45 - LOGIN FAILED - user:root - ip:198.51.100.22
"""

# Write log file using context manager
with open('security.log', 'w') as f:
    f.write(log_entries)

print("Log file created.\n")

# Read and analyze the log file
print("=== Security Log Analyzer ===\n")

failed_attempts = {}  # Track failed logins by IP

with open('security.log', 'r') as f:
    for line in f:
        if 'LOGIN FAILED' in line:
            # Extract IP address (simple parsing)
            parts = line.split('ip:')
            if len(parts) > 1:
                ip = parts[1].strip()

                # Count failed attempts per IP
                if ip in failed_attempts:
                    failed_attempts[ip] += 1
                else:
                    failed_attempts[ip] = 1

# Display results
print("Failed Login Attempts by IP:")
for ip, count in failed_attempts.items():
    status = "⚠️  ALERT" if count >= 3 else "ℹ️  Monitor"
    print(f"{status} - {ip}: {count} attempts")

# Write alert report
print("\nGenerating security report...")

with open('security_report.txt', 'w') as f:
    f.write("=== Security Alert Report ===\n")
    f.write(f"Generated: 2024-01-08\n\n")

    for ip, count in failed_attempts.items():
        if count >= 3:
            f.write(f"CRITICAL: Possible brute force from {ip} ({count} attempts)\n")

print("Report written to security_report.txt")

# Append additional finding
with open('security_report.txt', 'a') as f:
    f.write("\n--- Additional Notes ---\n")
    f.write("Recommend blocking 203.0.113.45 at firewall level.\n")

print("Additional notes appended to report.")