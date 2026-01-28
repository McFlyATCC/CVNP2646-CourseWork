# threat_intel_parser.py
# Parse JSON threat intelligence feed

import json

# Simulate a threat intelligence feed (normally from API)
threat_feed_json = '''
{
  "feed_name": "CyberThreat Daily",
  "generated": "2024-01-08T14:30:00Z",
  "threats": [
    {
      "ip": "203.0.113.45",
      "type": "brute_force",
      "severity": "high",
      "first_seen": "2024-01-07",
      "attacks_count": 156
    },
    {
      "ip": "198.51.100.22",
      "type": "port_scan",
      "severity": "medium",
      "first_seen": "2024-01-08",
      "attacks_count": 23
    },
    {
      "ip": "192.0.2.10",
      "type": "malware_distribution",
      "severity": "critical",
      "first_seen": "2024-01-06",
      "attacks_count": 489
    }
  ],
  "total_threats": 3
}
'''

print("=== Threat Intelligence Parser ===\n")

# Parse JSON string to Python dict
feed_data = json.loads(threat_feed_json)

print(f"Feed: {feed_data['feed_name']}")
print(f"Generated: {feed_data['generated']}")
print(f"Total Threats: {feed_data['total_threats']}\n")

print("High-Severity Threats:")
print("-" * 50)

# Process each threat
for threat in feed_data['threats']:
    # Filter for high and critical severity
    if threat['severity'] in ['high', 'critical']:
        print(f"\n⚠️  {threat['severity'].upper()}")
        print(f"   IP: {threat['ip']}")
        print(f"   Type: {threat['type']}")
        print(f"   Attacks: {threat['attacks_count']}")
        print(f"   First Seen: {threat['first_seen']}")

# Create blocklist from critical threats
blocklist = {
    "blocklist_name": "Critical Threats",
    "generated": "2024-01-08",
    "ips": []
}

for threat in feed_data['threats']:
    if threat['severity'] == 'critical':
        blocklist['ips'].append({
            "ip": threat['ip'],
            "reason": threat['type'],
            "attacks": threat['attacks_count']
        })

# Write blocklist to JSON file
with open('blocklist.json', 'w') as f:
    json.dump(blocklist, f, indent=2)

print("\n\nBlocklist generated: blocklist.json")

# Read and display the blocklist
with open('blocklist.json', 'r') as f:
    saved_blocklist = json.load(f)

print("\nBlocklist contents:")
print(json.dumps(saved_blocklist, indent=2))