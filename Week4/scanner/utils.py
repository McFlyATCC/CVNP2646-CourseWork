# utils.py
# Security utility functions

def validate_ip(ip):
    """Validate IPv4 address format"""
    parts = ip.split('.')

    if len(parts) != 4:
        return False

    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False

def calculate_threat_score(attacks, severity):
    """Calculate threat score from attacks and severity"""
    severity_multiplier = {
        'low': 1,
        'medium': 2,
        'high': 3,
        'critical': 5
    }

    multiplier = severity_multiplier.get(severity, 1)
    base_score = min(attacks, 100)  # Cap at 100

    return min(base_score * multiplier, 100)