#!/usr/bin/env python3
"""
Patch Risk Pipeline (Parts 1–6, single file)
-------------------------------------------
Loads a 20-host inventory (JSON), derives days_since_patch, computes risk
scores/levels, identifies high-risk systems, and generates JSON/Text/HTML
reports suitable for management and automation.

Usage:
  python patch_risk_pipeline.py hosts.json \
      --threshold 50 \
      --json risk_report.json \
      --text risk_summary.txt \
      --html risk_report.html \
      --enriched enriched_hosts.json

Input JSON shape:
  - Either a list of host objects, or {"hosts": [...]} wrapper.
  - Host fields include (sample):
    {
      "hostname": "FIN-WKS-001",
      "ip_address": "10.10.10.11",
      "os": "Windows 11 Pro",
      "os_version": "23H2",
      "last_patch_date": "2024-08-15",
      "criticality": "high",
      "environment": "production",
      "department": "Finance",
      "owner": "jsmith@company.com",
      "tags": ["pci-scope", "internet-facing"]
    }

Outputs:
  - JSON: High Risk Host Assessment
  - Text: Executive-style summary
  - HTML: Color-coded, sortable table
  - Enriched: (optional) list of hosts with derived fields
"""
from __future__ import annotations
from pathlib import Path 
from typing import List, Dict, Any
from datetime import datetime
import json
import html as html_lib
import argparse

# =====================================
# Part 1: Data Loading & Derived Values
# =====================================
DATE_FMT = '%Y-%m-%d'


def load_inventory(filepath: str) -> List[Dict[str, Any]]:
    """Load JSON inventory and return a list of host dicts.
    Accepts list at top-level or object with 'hosts' key.
    """
    p = Path(filepath)
    if not p.exists():
        raise FileNotFoundError(f"Inventory file not found: {filepath}")
    with p.open('r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, list):
        hosts = data
    elif isinstance(data, dict) and 'hosts' in data and isinstance(data['hosts'], list):
        hosts = data['hosts']
    else:
        raise ValueError("Inventory JSON must be a list or an object with a 'hosts' array")
    for i, h in enumerate(hosts):
        if not isinstance(h, dict):
            raise ValueError(f"Host entry at index {i} is not an object: {type(h)}")
    return hosts


def calculate_days_since_patch(host: Dict[str, Any], now: datetime | None = None) -> int | None:
    """Parse last_patch_date ('%Y-%m-%d'), compute days from now. Return int or None."""
    if now is None:
        now = datetime.now()
    date_str = host.get('last_patch_date')
    if not date_str:
        return None
    try:
        last_patch = datetime.strptime(date_str, DATE_FMT)
        delta = now - last_patch
        return delta.days
    except Exception:
        return None


def add_days_since_patch(hosts: List[Dict[str, Any]], now: datetime | None = None) -> List[Dict[str, Any]]:
    for h in hosts:
        h['days_since_patch'] = calculate_days_since_patch(h, now=now)
    return hosts

# ===============================
# Part 2: Filtering Functionality
# ===============================

def filter_by_os(hosts, os_type):
    """Case-insensitive partial match against 'os' field."""
    search = os_type.lower()
    return [h for h in hosts if search in (h.get('os', '') or '').lower()]


def filter_by_criticality(hosts, level):
    """Exact match (case-insensitive) on 'criticality'."""
    return [h for h in hosts if (h.get('criticality', '') or '').lower() == level.lower()]


def filter_by_environment(hosts, env):
    """Exact match (case-insensitive) on 'environment'."""
    return [h for h in hosts if (h.get('environment', '') or '').lower() == env.lower()]


def filter_critical_production(hosts):
    """criticality='critical' AND environment='production'"""
    return [
        h for h in hosts
        if (h.get('criticality', '') or '').lower() == 'critical' and (h.get('environment', '') or '').lower() == 'production'
    ]

# ===================================
# Part 3: Risk Scoring (0–100 points)
# ===================================
CRITICALITY_POINTS = {
    'critical': 40,
    'high': 25,
    'medium': 10,
    'low': 5,
}

ENVIRONMENT_POINTS = {
    'production': 15,
    'staging': 8,
    'development': 3,
}

TAG_POINTS = {
    'pci-scope': 10,
    'hipaa': 10,
    'internet-facing': 15,
}


def _points_for_patch_age(days_since_patch: int | None) -> int:
    if days_since_patch is None:
        return 0
    if days_since_patch > 90:
        return 30
    if days_since_patch > 60:
        return 20
    if days_since_patch > 30:
        return 10
    return 0


def calculate_risk_score(host: Dict[str, Any]) -> int:
    score = 0
    crit = (host.get('criticality', '') or '').lower()
    score += CRITICALITY_POINTS.get(crit, 0)

    score += _points_for_patch_age(host.get('days_since_patch'))

    env = (host.get('environment', '') or '').lower()
    score += ENVIRONMENT_POINTS.get(env, 0)

    tags = host.get('tags', []) or []
    tags_lower = {str(t).lower() for t in tags}
    for tag_key, pts in TAG_POINTS.items():
        if tag_key in tags_lower:
            score += pts

    return min(int(round(score)), 100)


def get_risk_level(score: int) -> str:
    if score >= 70:
        return 'critical'
    elif score >= 50:
        return 'high'
    elif score >= 25:
        return 'medium'
    else:
        return 'low'


def add_risk_fields(hosts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for h in hosts:
        rs = calculate_risk_score(h)
        h['risk_score'] = rs
        h['risk_level'] = get_risk_level(rs)
    return hosts

# ======================================
# Part 4: High-Risk Identification/Sort
# ======================================

def get_high_risk_hosts(hosts, threshold=50):
    filtered = [h for h in hosts if h.get('risk_score', 0) >= threshold]
    return sorted(filtered, key=lambda h: h['risk_score'], reverse=True)

# ==============================
# Part 5: Report Generation I/O
# ==============================
ISO_TS = '%Y-%m-%dT%H:%M:%S'
HUMAN_TS = '%Y-%m-%d %H:%M:%S'


def _now_iso() -> str:
    return datetime.now().strftime(ISO_TS)


def _now_human() -> str:
    return datetime.now().strftime(HUMAN_TS)


def _risk_distribution(hosts: List[Dict[str, Any]]) -> Dict[str, int]:
    dist = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for h in hosts:
        lvl = (h.get('risk_level', '') or '').lower()
        if lvl in dist:
            dist[lvl] += 1
    return dist


def _count_over_patch_age(hosts: List[Dict[str, Any]], days: int) -> int:
    return sum(1 for h in hosts if isinstance(h.get('days_since_patch'), int) and h['days_since_patch'] > days)


def _top_n_hosts(hosts: List[Dict[str, Any]], n: int = 5) -> List[Dict[str, Any]]:
    return sorted(hosts, key=lambda h: (h.get('risk_score', 0), h.get('days_since_patch') or -1, str(h.get('hostname',''))), reverse=True)[:n]


def _format_tags(tags: Any) -> str:
    if not tags:
        return ""
    return ", ".join(str(t) for t in tags)


def generate_json_report(hosts: List[Dict[str, Any]], high_risk_hosts: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_hosts = len(hosts)
    total_high = len(high_risk_hosts)
    dist = _risk_distribution(hosts)

    def _project(h: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "hostname": h.get("hostname"),
            "risk_score": h.get("risk_score"),
            "risk_level": h.get("risk_level"),
            "days_since_patch": h.get("days_since_patch"),
            "criticality": h.get("criticality"),
            "environment": h.get("environment"),
            "tags": h.get("tags", []),
        }

    return {
        "report_date": _now_iso(),
        "report_type": "High Risk Host Assessment",
        "total_hosts": total_hosts,
        "total_high_risk": total_high,
        "risk_distribution": dist,
        "high_risk_hosts": [_project(h) for h in sorted(high_risk_hosts, key=lambda x: x.get('risk_score', 0), reverse=True)],
    }


def generate_text_summary(hosts: List[Dict[str, Any]], high_risk_hosts: List[Dict[str, Any]]) -> str:
    total_hosts = len(hosts)
    total_high = len(high_risk_hosts)
    pct_high = (total_high / total_hosts * 100.0) if total_hosts else 0.0
    dist = _risk_distribution(hosts)
    over_90 = _count_over_patch_age(hosts, 90)
    top5 = _top_n_hosts(high_risk_hosts, 5)

    lines = []
    lines.append("=" * 64)
    lines.append("          WEEKLY PATCH COMPLIANCE SUMMARY REPORT")
    lines.append("=" * 64)
    lines.append("")
    lines.append(f"Generated: {_now_human()}")
    lines.append("")
    lines.append("EXECUTIVE SUMMARY")
    lines.append("-" * 64)
    lines.append(f"Total Systems Analyzed:        {total_hosts}")
    lines.append(f"High-Risk Systems Identified:  {total_high} ({pct_high:.1f}%)")
    lines.append(f"Critical Priority Systems:     {dist.get('critical', 0)}")
    lines.append(f"Immediate Action Required:     {over_90} systems >90 days unpatched")
    lines.append("")
    lines.append("RISK DISTRIBUTION")
    lines.append("-" * 64)
    lines.append(f"Critical (≥70 points):         {dist.get('critical', 0)} systems")
    lines.append(f"High (50-69 points):           {dist.get('high', 0)} systems")
    lines.append(f"Medium (25-49 points):         {dist.get('medium', 0)} systems")
    lines.append(f"Low (<25 points):              {dist.get('low', 0)} systems")
    lines.append("")
    lines.append("TOP 5 HIGHEST RISK SYSTEMS")
    lines.append("-" * 64)

    if not top5:
        lines.append("(No high-risk systems found above threshold.)")
    else:
        for i, h in enumerate(top5, start=1):
            hostname = h.get('hostname', 'N/A')
            score = h.get('risk_score', 0)
            level = str(h.get('risk_level', '')).capitalize() or 'N/A'
            days = h.get('days_since_patch', 'N/A')
            env = h.get('environment', 'N/A')
            tags = _format_tags(h.get('tags'))
            lines.append(f"{i}. {hostname} (Score: {score}, {level})")
            lines.append(f"   Last Patched: {days} days ago | {str(env).capitalize()} | Tags: {tags}")
            lines.append("   ")

    lines.append("RECOMMENDED ACTIONS")
    lines.append("-" * 64)
    lines.append("IMMEDIATE (Next 48 hours):")
    lines.append("• Patch critical-risk systems that are internet-facing and in PCI scope")
    lines.append("• Review emergency change control procedures")
    lines.append("")
    lines.append("THIS WEEK (Next 7 days):")
    lines.append("• Schedule maintenance windows for high-risk production systems")
    lines.append("• Test patches in staging environment first")
    lines.append("")
    lines.append("THIS MONTH (Next 30 days):")
    lines.append("• Implement automated patch deployment for dev/test systems")
    lines.append("• Review and update patch management SOP")
    lines.append("")
    lines.append("COMPLIANCE NOTES")
    lines.append("-" * 64)
    lines.append("CIS Control 7.3: Critical vulnerabilities should be remediated within 15 days.")
    lines.append("PCI-DSS 6.2: Systems in PCI scope should be patched within 30 days of vendor release.")
    lines.append("=" * 64)

    return "\n".join(lines)


def generate_html_report(hosts: List[Dict[str, Any]]) -> str:
    dist = _risk_distribution(hosts)
    total_hosts = len(hosts)

    def esc(x: Any) -> str:
        return html_lib.escape(str(x)) if x is not None else ''

    def row_class(level: str) -> str:
        lvl = (level or '').lower()
        if lvl == 'critical':
            return 'row-critical'
        if lvl == 'high':
            return 'row-high'
        if lvl == 'medium':
            return 'row-medium'
        return 'row-low'

    sorted_hosts = sorted(hosts, key=lambda h: h.get('risk_score', 0), reverse=True)

    rows_html = []
    for h in sorted_hosts:
        tags = ", ".join(str(t) for t in (h.get('tags') or []))
        tr = f"""
        <tr class='{row_class(h.get('risk_level'))}'>
            <td>{esc(h.get('hostname', ''))}</td>
            <td>{esc(h.get('ip_address', ''))}</td>
            <td>{esc(h.get('os', ''))}</td>
            <td>{esc(h.get('environment', ''))}</td>
            <td>{esc(h.get('criticality', ''))}</td>
            <td data-num='{esc(h.get('days_since_patch', ''))}'>{esc(h.get('days_since_patch', ''))}</td>
            <td data-num='{esc(h.get('risk_score', ''))}'>{esc(h.get('risk_score', ''))}</td>
            <td>{esc(h.get('risk_level', ''))}</td>
            <td>{esc(tags)}</td>
        </tr>
        """
        rows_html.append(tr)

    html = f"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>High-Risk Host Assessment</title>
<style>
    :root {{
        --bg: #0f172a; --card: #111827; --text: #e5e7eb; --muted: #9ca3af;
        --critical: #fee2e2; --critical-border: #dc2626;
        --high: #ffedd5; --high-border: #ea580c;
        --medium: #fef3c7; --medium-border: #d97706;
        --low: #ecfccb; --low-border: #65a30d; --accent: #3b82f6;
    }}
    body {{ background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 24px; }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    .header {{ display:flex; align-items:center; justify-content:space-between; margin-bottom: 16px; }}
    .title {{ font-size: 24px; font-weight: 700; }}
    .subtitle {{ color: var(--muted); font-size: 14px; }}
    .cards {{ display:grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 16px 0; }}
    .card {{ background: var(--card); padding: 16px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.25); }}
    .card h3 {{ margin: 0 0 8px 0; font-size: 14px; color: var(--muted); font-weight: 600; }}
    .card .value {{ font-size: 22px; font-weight: 700; }}
    table {{ width:100%; border-collapse: collapse; background: var(--card); border-radius: 12px; overflow: hidden; }}
    thead th {{ position: sticky; top:0; background: #0b1220; color: var(--text); text-align:left; padding:10px; font-size: 13px; cursor: pointer; }}
    tbody td {{ padding: 10px; border-top: 1px solid rgba(255,255,255,0.06); font-size: 13px; }}
    tr.row-critical {{ background: var(--critical); color: #7f1d1d; border-left: 4px solid var(--critical-border); }}
    tr.row-high {{ background: var(--high); color: #7c2d12; border-left: 4px solid var(--high-border); }}
    tr.row-medium {{ background: var(--medium); color: #78350f; border-left: 4px solid var(--medium-border); }}
    tr.row-low {{ background: var(--low); color: #365314; border-left: 4px solid var(--low-border); }}
    .note {{ color: var(--muted); font-size: 12px; margin-top: 8px; }}
</style>
<script>
    function sortTable(n) {{
      const table = document.getElementById('riskTable');
      const tbody = table.tBodies[0];
      const rows = Array.from(tbody.rows);
      const ascending = table.getAttribute('data-sort-col') == n && table.getAttribute('data-sort-dir') == 'asc' ? false : true;
      rows.sort((a, b) => {{
        const aCell = a.cells[n];
        const bCell = b.cells[n];
        const aNum = aCell.getAttribute('data-num');
        const bNum = bCell.getAttribute('data-num');
        let cmp;
        if (aNum !== null && aNum !== '' && !isNaN(parseFloat(aNum)) && bNum !== null && bNum !== '' && !isNaN(parseFloat(bNum))) {{
          cmp = parseFloat(aNum) - parseFloat(bNum);
        }} else {{
          cmp = aCell.textContent.localeCompare(bCell.textContent, undefined, {{ sensitivity: 'base' }});
        }}
        return ascending ? cmp : -cmp;
      }});
      rows.forEach(r => tbody.appendChild(r));
      table.setAttribute('data-sort-col', n);
      table.setAttribute('data-sort-dir', ascending ? 'asc' : 'desc');
    }}
</script>
</head>
<body>
  <div class="container">
    <div class="header">
      <div>
        <div class="title">High Risk Host Assessment</div>
        <div class="subtitle">Generated: {_now_human()}</div>
      </div>
    </div>
    <div class="cards">
      <div class="card"><h3>Total Hosts</h3><div class="value">{total_hosts}</div></div>
      <div class="card"><h3>Critical</h3><div class="value">{dist.get('critical',0)}</div></div>
      <div class="card"><h3>High</h3><div class="value">{dist.get('high',0)}</div></div>
      <div class="card"><h3>Medium</h3><div class="value">{dist.get('medium',0)}</div></div>
      <div class="card"><h3>Low</h3><div class="value">{dist.get('low',0)}</div></div>
    </div>
    <table id="riskTable" data-sort-col="6" data-sort-dir="desc">
      <thead>
        <tr>
          <th onclick="sortTable(0)">Hostname</th>
          <th onclick="sortTable(1)">IP Address</th>
          <th onclick="sortTable(2)">OS</th>
          <th onclick="sortTable(3)">Environment</th>
          <th onclick="sortTable(4)">Criticality</th>
          <th onclick="sortTable(5)">Days Since Patch</th>
          <th onclick="sortTable(6)">Risk Score</th>
          <th onclick="sortTable(7)">Risk Level</th>
          <th onclick="sortTable(8)">Tags</th>
        </tr>
      </thead>
      <tbody>
        {''.join(rows_html)}
      </tbody>
    </table>
    <div class="note">CIS Control 7.3: Remediate critical vulnerabilities within ~15 days. PCI-DSS 6.2: Patch in-scope systems within ~30 days of vendor release.</div>
  </div>
</body>
</html>
"""
    return html


def write_reports_files(hosts: List[Dict[str, Any]], high_risk_hosts: List[Dict[str, Any]],
                        json_path: str = 'risk_report.json',
                        text_path: str = 'risk_summary.txt',
                        html_path: str = 'risk_report.html') -> None:
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(generate_json_report(hosts, high_risk_hosts), f, indent=2)
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(generate_text_summary(hosts, high_risk_hosts))
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(generate_html_report(hosts))

# ================================
# Part 6: Orchestration/Pipeline
# ================================

def analyze_inventory(hosts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add days_since_patch, risk_score, risk_level to each host (in place)."""
    add_days_since_patch(hosts)
    add_risk_fields(hosts)
    return hosts

# ================================
# CLI Entrypoint
# ================================

def main():
    parser = argparse.ArgumentParser(description='End-to-end Patch Risk Pipeline (Parts 1–6).')
    parser.add_argument('input', help='Path to inventory JSON (list or {"hosts": [...]})')
    parser.add_argument('--threshold', type=int, default=50, help='High-risk threshold (default 50)')
    parser.add_argument('--json', default='risk_report.json', help='Output JSON report path')
    parser.add_argument('--text', default='risk_summary.txt', help='Output text summary path')
    parser.add_argument('--html', default='risk_report.html', help='Output HTML report path')
    parser.add_argument('--enriched', default='enriched_hosts.json', help='Optional enriched hosts output path')
    args = parser.parse_args()

    hosts = load_inventory(args.input)
    analyze_inventory(hosts)
    high = get_high_risk_hosts(hosts, threshold=args.threshold)

    # Write the three reports
    write_reports_files(hosts, high, args.json, args.text, args.html)

    # Write enriched list (optional always-on here, adjustable via args)
    if args.enriched:
        with open(args.enriched, 'w', encoding='utf-8') as f:
            json.dump(hosts, f, indent=2)

    print(f"Reports written: {args.json}, {args.text}, {args.html}")
    print(f"Enriched hosts written: {args.enriched}")


if __name__ == '__main__':
    main()
