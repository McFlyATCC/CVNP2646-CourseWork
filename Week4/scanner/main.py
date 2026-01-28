# main.py
# Main script using modular security functions

from utils import validate_ip, calculate_threat_score
from file_ops import load_blocklist, save_report

print("=== Modular IP Blocklist Checker ===\n")

# Load blocklist using file_ops module
blocklist = load_blocklist('blocklist.json')

if blocklist:
    print(f"Loaded blocklist: {blocklist['blocklist_name']}")
    print(f"Total blocked IPs: {len(blocklist['ips'])}\n")

    # Process each IP using utils module
    for entry in blocklist['ips']:
        ip = entry['ip']

        # Validate IP using utils module
        if validate_ip(ip):
            # Calculate threat score
            score = calculate_threat_score(
                entry['attacks'],
                'critical'  # All blocklist IPs are critical
            )

            print(f"✓ {ip}")
            print(f"  Reason: {entry['reason']}")
            print(f"  Attacks: {entry['attacks']}")
            print(f"  Threat Score: {score}/100\n")
        else:
            print(f"❌ Invalid IP format: {ip}\n")

    # Generate summary report using file_ops module
    summary = {
        "total_blocked": len(blocklist['ips']),
        "average_attacks": sum(e['attacks'] for e in blocklist['ips']) / len(blocklist['ips'])
    }

    save_report('summary.json', summary)
    print("Summary report saved to summary.json")