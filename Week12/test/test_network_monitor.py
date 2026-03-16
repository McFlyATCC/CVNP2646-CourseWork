# test_network_monitor.py

import pytest
from network_monitor import (
    NetworkConfig,
    parse_packet_line,
    detect_port_scan,
    detect_syn_flood,
    analyze_traffic,
)


# -------------------------------------------------
# Fixtures
# -------------------------------------------------

@pytest.fixture
def sample_config():
    return NetworkConfig(
        port_scan_threshold=25,
        syn_flood_threshold=100
    )


@pytest.fixture
def valid_packet_line():
    return "192.168.1.5,10.0.0.1,54321,443,TCP,SYN"


@pytest.fixture
def sample_packets():
    return [
        {
            'src_ip': '192.168.1.5',
            'dst_ip': '10.0.0.1',
            'src_port': 54321,
            'dst_port': 443,
            'protocol': 'TCP',
            'flags': 'SYN'
        },
        {
            'src_ip': '192.168.1.5',
            'dst_ip': '10.0.0.1',
            'src_port': 54322,
            'dst_port': 80,
            'protocol': 'TCP',
            'flags': 'SYN'
        },
    ]


# -------------------------------------------------
# Parser Tests
# -------------------------------------------------

def test_parse_valid_packet(valid_packet_line):
    packet = parse_packet_line(valid_packet_line)

    assert packet['src_ip'] == "192.168.1.5"
    assert packet['dst_ip'] == "10.0.0.1"
    assert packet['src_port'] == 54321
    assert packet['dst_port'] == 443
    assert packet['protocol'] == "TCP"
    assert packet['flags'] == "SYN"


def test_parse_invalid_too_few_fields():
    with pytest.raises(ValueError):
        parse_packet_line("192.168.1.5,10.0.0.1,443")


def test_parse_invalid_too_many_fields():
    with pytest.raises(ValueError):
        parse_packet_line(
            "192.168.1.5,10.0.0.1,54321,443,TCP,SYN,EXTRA"
        )


def test_parse_non_numeric_port():
    with pytest.raises(ValueError):
        parse_packet_line(
            "192.168.1.5,10.0.0.1,abc,443,TCP,SYN"
        )


def test_parse_empty_string():
    with pytest.raises(ValueError):
        parse_packet_line("")


def test_parse_extra_whitespace():
    line = " 192.168.1.5 , 10.0.0.1 , 54321 , 443 , TCP , SYN "
    packet = parse_packet_line(line)

    assert packet['src_ip'] == "192.168.1.5"
    assert packet['dst_ip'] == "10.0.0.1"


# -------------------------------------------------
# Detection Tests
# -------------------------------------------------

def test_port_scan_below_threshold(sample_packets, sample_config):
    assert detect_port_scan(
        sample_packets,
        "192.168.1.5",
        sample_config.port_scan_threshold
    ) is False


def test_port_scan_above_threshold(sample_config):
    packets = [
        {
            'src_ip': '192.168.1.5',
            'dst_port': port,
            'protocol': 'TCP'
        }
        for port in range(1, 31)
    ]

    assert detect_port_scan(
        packets,
        "192.168.1.5",
        sample_config.port_scan_threshold
    ) is True


def test_syn_flood_above_threshold(sample_config):
    packets = [
        {
            'src_ip': '192.168.1.5',
            'protocol': 'TCP',
            'flags': 'SYN'
        }
        for _ in range(150)
    ]

    assert detect_syn_flood(
        packets,
        "192.168.1.5",
        sample_config.syn_flood_threshold
    ) is True


# -------------------------------------------------
# Integration Tests
# -------------------------------------------------

def test_analyze_traffic(sample_packets, sample_config):
    results = analyze_traffic(sample_packets, sample_config)

    assert results['total_packets'] == len(sample_packets)
    assert isinstance(results['port_scans'], list)
    assert isinstance(results['syn_floods'], list)


def test_analyze_empty_traffic(sample_config):
    results = analyze_traffic([], sample_config)

    assert results['total_packets'] == 0
    assert results['port_scans'] == []
    assert results['syn_floods'] == []