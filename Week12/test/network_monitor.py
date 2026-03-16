# network_monitor.py
"""
Core network monitoring logic.

This module is intentionally:
- Pure (no file I/O)
- Free of global state
- Designed for pytest unit testing
"""

from dataclasses import dataclass
from typing import List, Dict


# -------------------------------------------------
# Configuration
# -------------------------------------------------

@dataclass
class NetworkConfig:
    port_scan_threshold: int
    syn_flood_threshold: int


# -------------------------------------------------
# Parsing
# -------------------------------------------------

def parse_packet_line(line: str) -> Dict:
    """
    Parse a packet log line into a dictionary.

    Expected format:
    src_ip,dst_ip,src_port,dst_port,protocol,flags
    """
    if not line or not line.strip():
        raise ValueError("Empty packet line")

    parts = [part.strip() for part in line.split(",")]

    if len(parts) != 6:
        raise ValueError("Invalid number of fields")

    src_ip, dst_ip, src_port, dst_port, protocol, flags = parts

    try:
        src_port = int(src_port)
        dst_port = int(dst_port)
    except ValueError:
        raise ValueError("Port values must be integers")

    return {
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "src_port": src_port,
        "dst_port": dst_port,
        "protocol": protocol,
        "flags": flags,
    }


# -------------------------------------------------
# Detection Logic
# -------------------------------------------------

def detect_port_scan(
    packets: List[Dict],
    src_ip: str,
    threshold: int
) -> bool:
    """
    Detect port scan by counting unique destination ports.
    """
    unique_ports = {
        packet["dst_port"]
        for packet in packets
        if packet.get("src_ip") == src_ip
        and "dst_port" in packet
    }

    return len(unique_ports) > threshold


def detect_syn_flood(
    packets: List[Dict],
    src_ip: str,
    threshold: int
) -> bool:
    """
    Detect SYN flood by counting TCP SYN packets.
    """
    syn_count = sum(
        1
        for packet in packets
        if packet.get("src_ip") == src_ip
        and packet.get("protocol") == "TCP"
        and "SYN" in packet.get("flags", "")
    )

    return syn_count > threshold


# -------------------------------------------------
# Analysis Pipeline
# -------------------------------------------------

def analyze_traffic(
    packets: List[Dict],
    config: NetworkConfig
) -> Dict:
    """
    Run full traffic analysis.
    """
    src_ips = {
        packet["src_ip"]
        for packet in packets
        if "src_ip" in packet
    }

    port_scans = []
    syn_floods = []

    for ip in src_ips:
        if detect_port_scan(
            packets, ip, config.port_scan_threshold
        ):
            port_scans.append(ip)

        if detect_syn_flood(
            packets, ip, config.syn_flood_threshold
        ):
            syn_floods.append(ip)

    return {
        "total_packets": len(packets),
        "port_scans": port_scans,
        "syn_floods": syn_floods,
    }
