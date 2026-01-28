
#!/usr/bin/env python3
# subnet_calculator.py
# Calculates network information for IPv4/IPv6 subnets using Python's ipaddress

import ipaddress

def calculate_subnet(network_ip, subnet_mask):
    """
    Calculates subnet information based on CIDR notation using ipaddress.

    Parameters:
    - network_ip: The network (or host) address, e.g., "192.168.1.0" or "2001:db8::"
    - subnet_mask: Integer CIDR prefix length (e.g., 24 for /24, 64 for /64)

    Returns: Dictionary with subnet information (IPv4 or IPv6 aware)
    """
    # Build CIDR string and parse network. strict=False allows host IPs (auto-correct to network boundary).
    try:
        cidr = f"{network_ip}/{subnet_mask}"
        net = ipaddress.ip_network(cidr, strict=False)
    except ValueError as e:
        raise ValueError(f"Invalid network/prefix combination: {cidr}. {e}")

    # Validate mask range per IP version
    if isinstance(net, ipaddress.IPv4Network):
        if not (0 <= subnet_mask <= 32):
            raise ValueError("IPv4 subnet mask must be between 0 and 32.")
    else:  # IPv6
        if not (0 <= subnet_mask <= 128):
            raise ValueError("IPv6 prefix length must be between 0 and 128.")

    total_ips = net.num_addresses

    # Compute usable hosts & boundaries
    if isinstance(net, ipaddress.IPv4Network):
        # Classic IPv4 host-subnetting: /31 and /32 have 0 traditional usable hosts
        if net.prefixlen in (31, 32):
            usable_hosts = 0
            first_usable = None
            last_usable = None
        else:
            usable_hosts = max(total_ips - 2, 0)
            first_usable = str(net.network_address + 1)
            last_usable = str(net.broadcast_address - 1)

        broadcast = str(net.broadcast_address)
        netmask = str(net.netmask)
        wildcard_mask = str(ipaddress.IPv4Address(int(net.hostmask)))

        # Legacy class detection (kept for compatibility/printing)
        first_octet = int(str(net.network_address).split('.')[0])
        if 1 <= first_octet <= 127:
            network_class = "A"
        elif 128 <= first_octet <= 191:
            network_class = "B"
        elif 192 <= first_octet <= 223:
            network_class = "C"
        else:
            network_class = "Unknown"

    else:
        # IPv6: No broadcast; all addresses are typically usable in principle
        usable_hosts = total_ips
        first_usable = str(net.network_address)
        # Avoid materializing all hosts for huge subnets; approximate last usable via math:
        # last usable = network_address + (num_addresses - 1)
        last_usable = str(net.network_address + (net.num_addresses - 1))
        broadcast = None
        netmask = None
        wildcard_mask = None
        network_class = "N/A (IPv6)"

    return {
        'version': 'IPv6' if isinstance(net, ipaddress.IPv6Network) else 'IPv4',
        'cidr': str(net),  # normalized network/prefix
        'network_ip': str(net.network_address),
        'subnet_mask': net.prefixlen,
        'netmask': netmask,
        'wildcard_mask': wildcard_mask,
        'broadcast': broadcast,
        'first_usable': first_usable,
        'last_usable': last_usable,
        'total_ips': total_ips,
        'usable_hosts': usable_hosts,
        'network_class': network_class,
    }


def parse_cidr_mask_input(user_input: str) -> int:
    """
    Accepts input like '24' or '/24' (whitespace ok) and returns an int.
    Allows up to 128 to accommodate IPv6.
    Range-by-version validation is handled in calculate_subnet().
    """
    if user_input is None:
        raise ValueError("Empty subnet mask input.")
    s = user_input.strip()
    if s.startswith('/'):
        s = s[1:]  # drop leading slash
    if not s.isdigit():
        raise ValueError("Subnet mask must be a number like 24 or /24.")
    mask = int(s)
    if not (0 <= mask <= 128):
        raise ValueError("Subnet mask must be between 0 and 128.")
    return mask


# Main program
print("=" * 60)
print("NETWORK SUBNET CALCULATOR")
print("=" * 60 + "\n")

# Test Case 1: /24 subnet (common for small networks)
print("Test Case 1: Common Small Network")
print("-" * 60)
result1 = calculate_subnet("192.168.1.0", 24)
print(f"Network:           {result1['cidr']}")
print(f"IP Version:        {result1['version']}")
print(f"Network Class:     Class {result1['network_class']}")
print(f"Netmask:           {result1['netmask']}")
print(f"Wildcard Mask:     {result1['wildcard_mask']}")
print(f"Broadcast:         {result1['broadcast']}")
print(f"First Usable:      {result1['first_usable']}")
print(f"Last Usable:       {result1['last_usable']}")
print(f"Total IP Addresses:{result1['total_ips']:,}")
print(f"Usable Host IPs:   {result1['usable_hosts']:,}")
print(f"Calculation: 2^(32-{result1['subnet_mask']}) = 2^{32-result1['subnet_mask']} = {result1['total_ips']}\n")

# Test Case 2: /28 subnet (smaller subnet for security segmentation)
print("Test Case 2: Security Segmented Subnet")
print("-" * 60)
result2 = calculate_subnet("10.0.10.0", 28)
print(f"Network:           {result2['cidr']}")
print(f"IP Version:        {result2['version']}")
print(f"Network Class:     Class {result2['network_class']}")
print(f"Netmask:           {result2['netmask']}")
print(f"Wildcard Mask:     {result2['wildcard_mask']}")
print(f"Broadcast:         {result2['broadcast']}")
print(f"First Usable:      {result2['first_usable']}")
print(f"Last Usable:       {result2['last_usable']}")
print(f"Total IP Addresses:{result2['total_ips']}")
print(f"Usable Host IPs:   {result2['usable_hosts']}")
print(f"Calculation: 2^(32-{result2['subnet_mask']}) = 2^{32-result2['subnet_mask']} = {result2['total_ips']}\n")

# Interactive mode
print("=" * 60)
print("INTERACTIVE MODE")
print("=" * 60)

# Get user input
network = input("\nEnter network IP address (IPv4 or IPv6, e.g., 172.16.0.0 or 2001:db8::): ")
mask_input = input("Enter subnet mask (CIDR, e.g., 24 or /24; IPv6 e.g., 64 or /64): ")

try:
    mask = parse_cidr_mask_input(mask_input)
    # Calculate and display results
    result = calculate_subnet(network, mask)

    print("\n" + "=" * 60)
    print("SUBNET CALCULATION RESULTS")
    print("=" * 60)
    print(f"Network:           {result['cidr']}")
    print(f"IP Version:        {result['version']}")
    print(f"Network Class:     Class {result['network_class']}")
    if result['version'] == 'IPv4':
        print(f"Netmask:           {result['netmask']}")
        print(f"Wildcard Mask:     {result['wildcard_mask']}")
        print(f"Broadcast:         {result['broadcast']}")
        print(f"First Usable:      {result['first_usable']}")
        print(f"Last Usable:       {result['last_usable']}")
    else:
        print("Netmask:           N/A (IPv6)")
        print("Wildcard Mask:     N/A (IPv6)")
        print("Broadcast:         N/A (IPv6)")
        print(f"First Address:     {result['first_usable']}")
        print(f"Last Address:      {result['last_usable']}")
    print(f"Total IP Addresses:{result['total_ips']:,}")
    print(f"Usable Host IPs:   {result['usable_hosts']:,}")
    print("=" * 60)

    # Security context
    print("\n💡 Security Note:")
    if result['total_ips'] > 256:
        print("   Large subnet - consider segmentation for security isolation")
    elif result['total_ips'] <= 16:
        print("   Small subnet - good for critical infrastructure isolation")
    else:
        print("   Medium subnet - suitable for departmental segmentation")

except ValueError as ve:
    print(f"\n[Error] {ve}")
except Exception as e:
    print(f"\n[Unexpected Error] {e}")
