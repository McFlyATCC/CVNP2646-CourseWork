import re, warnings
from collections import Counter

# --- Parser from Step 2 (robust) ---
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
TOKEN_RE = re.compile(
    r"""
    (?P<key>[A-Za-z_][A-Za-z0-9_\-]*)   # key
    =
    (
      \"(?P<dq>(?:\\.|[^\"])*)\"   # double-quoted value
      |
      '(?P<sq>(?:\\.|[^'])*)'      # single-quoted value
      |
      (?P<bare>[^\s]+)             # bareword value
    )
    """,
    re.VERBOSE,
)

def parse_log_line(
    line,
    *,
    normalize_keys: bool = True,
    collect_duplicates: bool = True,
    warn_on_junk: bool = True,
    allow_blank_timestamp: bool = True,
):
    """
    Robustly parse a single log line.

    Returns:
      - dict with 'timestamp' and parsed fields, or
      - None for unparseable lines (missing timestamp and no parsable fields).

    Guarantees:
      - Skips malformed key=value tokens.
      - Never raises (returns None on unexpected exceptions).
    """
    try:
        if not isinstance(line, str):
            line = "" if line is None else str(line)
        s = line.rstrip("\n")
        if s.strip() == "":
            return None
        if len(s) < 19:
            if warn_on_junk:
                warnings.warn("Missing 19-char timestamp region; line unparseable.")
            return None
        ts_field = s[:19]
        rest = s[19:].lstrip()
        if TIMESTAMP_RE.match(ts_field):
            timestamp = ts_field
        elif allow_blank_timestamp and ts_field.strip() == "":
            timestamp = None
            if warn_on_junk:
                warnings.warn("Blank timestamp encountered; setting timestamp=None.")
        else:
            if warn_on_junk:
                warnings.warn(f"Invalid/missing timestamp: '{ts_field}'")
            return None
        fields = {"timestamp": timestamp}
        pos = 0
        length = len(rest)
        while pos < length:
            m = TOKEN_RE.match(rest, pos)
            if m:
                key = m.group("key").lower() if normalize_keys else m.group("key")
                if m.group("dq") is not None:
                    val = m.group("dq").replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
                elif m.group("sq") is not None:
                    val = m.group("sq").replace("\\'", "'").replace('\\n', '\n').replace('\\t', '\t')
                else:
                    val = m.group("bare")
                if collect_duplicates:
                    if key in fields and key != "timestamp":
                        if not isinstance(fields[key], list):
                            fields[key] = [fields[key]]
                        fields[key].append(val)
                    else:
                        fields[key] = val
                else:
                    fields.setdefault(key, val)
                pos = m.end()
                while pos < length and rest[pos].isspace():
                    pos += 1
                continue
            next_space = rest.find(" ", pos)
            bad_token = rest[pos:] if next_space == -1 else rest[pos:next_space]
            if warn_on_junk and bad_token:
                warnings.warn(f"Skipping malformed token: '{bad_token}'")
            if next_space == -1:
                break
            pos = next_space + 1
            while pos < length and rest[pos].isspace():
                pos += 1
        has_kv = any(k for k in fields.keys() if k != "timestamp")
        if not has_kv and fields["timestamp"] is None:
            return None
        return fields
    except Exception as e:
        if warn_on_junk:
            warnings.warn(f"Parser error: {e}")
        return None

# --- Step 3 counting ---

def _as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]

def count_failed_logins(lines, *, warn_on_missing_fields=False):
    """
    Count FAIL login events by user and IP.

    - Only count events where any status equals FAIL (case-insensitive).
    - Accepts duplicate fields as lists.
    - Skips unparseable lines (parse_log_line returns None).
    """
    users_ctr = Counter()
    ips_ctr = Counter()
    seen = 0
    counted = 0
    skipped = 0

    for line in lines:
        parsed = parse_log_line(line, warn_on_junk=False)
        if parsed is None:
            skipped += 1
            continue
        seen += 1

        statuses = [s.upper() for s in _as_list(parsed.get('status'))]
        is_fail = any(s == 'FAIL' for s in statuses)
        if not is_fail:
            continue

        for u in _as_list(parsed.get('user')):
            if u:
                users_ctr[u] += 1
        for ip in _as_list(parsed.get('ip')):
            if ip:
                ips_ctr[ip] += 1

        counted += 1

    return {
        'users': users_ctr,
        'ips': ips_ctr,
        'total_fail': sum(users_ctr.values()) if users_ctr else sum(ips_ctr.values()),
        'seen': seen,
        'counted': counted,
        'skipped': skipped,
    }

# --- Test with your provided sample (includes a blank line) ---
sample = """2024-11-25 08:12:34 event=LOGIN status=SUCCESS user=jsmith ip=10.0.1.50 method=WEB
2024-11-25 08:15:22 event=LOGIN status=SUCCESS user=admin ip=10.0.1.10 method=SSH
2024-11-25 08:18:45 event=LOGIN status=SUCCESS user=alice ip=192.168.1.100 method=WEB
2024-11-25 08:22:10 event=LOGIN status=SUCCESS user=bob ip=172.16.0.50 method=SSH
2024-11-25 08:25:33 event=LOGIN status=SUCCESS user=charlie ip=10.0.2.75 method=WEB
2024-11-25 08:30:12 event=LOGIN status=FAIL user=admin ip=198.51.100.45 method=SSH
2024-11-25 08:30:15 event=LOGIN status=FAIL user=admin ip=198.51.100.45 method=SSH
2024-11-25 08:30:18 event=LOGIN status=FAIL user=root ip=198.51.100.45 method=SSH
2024-11-25 08:30:21 event=LOGIN status=FAIL user=admin ip=198.51.100.45 method=SSH
2024-11-25 08:30:24 event=LOGIN status=FAIL user=admin ip=198.51.100.45 method=SSH
2024-11-25 08:30:27 event=LOGIN status=FAIL user=administrator ip=198.51.100.45 method=SSH
2024-11-25 08:30:30 event=LOGIN status=FAIL user=admin ip=198.51.100.45 method=SSH
2024-11-25 08:35:10 event=LOGIN status user=admin ip=198.51.100.45 method=SSH
2024-11-25 event=LOGIN status=FAIL user=admin ip=198.51.100.45
2024-11-25 08:40:12 event=LOGIN status=FAIL user=root ip=203.0.113.89 method=SSH
2024-11-25 08:40:15 event=LOGIN status=FAIL user=administrator ip=203.0.113.89 method=SSH
2024-11-25 08:40:18 event=LOGIN status=FAIL user=admin ip=203.0.113.89 method=SSH
2024-11-25 08:42:30 event=LOGIN status=SUCCESS user=alice ip=192.168.1.100 method=WEB
2024-11-25 08:45:12 event=LOGIN status=FAIL user=admin ip=192.0.2.15 method=SSH
2024-11-25 08:45:15 event=LOGIN status=FAIL user=root ip=192.0.2.15 method=SSH
2024-11-25 08:45:18 event=LOGIN status=FAIL user=admin ip=192.0.2.15 method=SSH

2024-11-25 08:50:00 event=LOGIN status=SUCCESS user=bob ip=172.16.0.50 method=SSH
2024-11-25 08:52:00 event=LOGIN status=FAIL user=test ip=198.51.100.92 method=WEB
2024-11-25 08:54:00 event=LOGIN status=FAIL user=admin ip=198.51.100.45 method=SSH"""
lines = sample.splitlines()

stats = count_failed_logins(lines)
print("Users Counter:", stats['users'])
print("IPs Counter:", stats['ips'])
print("Most common users:", stats['users'].most_common())
print("Most common IPs:", stats['ips'].most_common())
print({k: v for k, v in stats.items() if k not in ('users','ips')})