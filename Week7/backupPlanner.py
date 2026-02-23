#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple, config-driven backup planner (DRY-RUN ONLY).
- Validates config at four levels (structure, required fields, types, values)
- Simulates backups by generating FAKE file lists (no filesystem scanning)
- Produces a readable report

Functions:
  - load_config(filepath) -> dict | None
  - validate_config(config) -> (bool, list[str])
  - simulate_backup(config) -> dict
  - generate_report(report_dict) -> str
  - main() -> CLI orchestration

Usage:
  python backup_planner.py --config config.json --dry-run
  python backup_planner.py --config config.json --dry-run --json-out report.json
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime
from typing import Any, Dict, List, Tuple, Optional

# -----------------------------
# Helpers
# -----------------------------

def iso_now() -> str:
    return datetime.now().isoformat(timespec="seconds")

def type_name(x: Any) -> str:
    return type(x).__name__

def clamp(n: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, n))

# -----------------------------
# Part 3: Function: load_config
# -----------------------------

def load_config(filepath: str) -> Optional[Dict[str, Any]]:
    """Load and parse JSON file. Returns dict or None on error."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: file not found: {filepath}")
        return None
    except json.JSONDecodeError as ex:
        print(f"Error: invalid JSON at line {ex.lineno}, column {ex.colno}: {ex.msg}")
        return None
    except Exception as ex:
        print(f"Error: could not read config: {ex}")
        return None

# --------------------------------
# Part 3: Function: validate_config
# --------------------------------

def validate_config(cfg: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate configuration across 4 levels.
    Returns: (is_valid, errors)
    - Collects ALL errors.
    """
    errors: List[str] = []

    # --- Level 1: Structure Validation ---
    if not isinstance(cfg, dict):
        errors.append(f"Top-level JSON must be an object, got {type_name(cfg)}")
        return False, errors  # can't proceed

    # --- Level 2: Required Fields ---
    # metadata is optional but plan_name is required (can be in metadata or top-level for flexibility)
    metadata = cfg.get("metadata", {})
    plan_name = metadata.get("plan_name") or cfg.get("plan_name")
    if plan_name is None:
        errors.append("Missing required field: 'plan_name'")

    if "sources" not in cfg:
        errors.append("Missing required field: 'sources'")
    if "destination" not in cfg:
        errors.append("Missing required field: 'destination'")

    # Early exits avoided—collect all errors

    # --- Level 3: Type Validation ---
    if plan_name is not None and not isinstance(plan_name, str):
        errors.append(f"'plan_name' must be a string, got {type_name(plan_name)}")

    sources = cfg.get("sources")
    if sources is not None and not isinstance(sources, list):
        errors.append(f"'sources' must be a list, got {type_name(sources)}")

    destination = cfg.get("destination")
    if destination is not None and not isinstance(destination, dict):
        errors.append(f"'destination' must be a dictionary, got {type_name(destination)}")

    # Options (optional)
    options = cfg.get("options")
    if options is not None and not isinstance(options, dict):
        errors.append(f"'options' must be a dictionary, got {type_name(options)}")

    # Early return if fundamental types are wrong
    if errors:
        return len(errors) == 0, errors

    # --- Level 4: Value Validation ---
    # Sources list present & non-empty
    if isinstance(sources, list):
        if len(sources) == 0:
            errors.append("Sources list cannot be empty")
        else:
            for idx, src in enumerate(sources):
                if not isinstance(src, dict):
                    errors.append(f"Source {idx}: must be an object, got {type_name(src)}")
                    continue
                # required: path
                if "path" not in src:
                    errors.append(f"Source {idx}: missing 'path' field")
                else:
                    if not isinstance(src["path"], str):
                        errors.append(f"Source {idx}: 'path' must be a string, got {type_name(src['path'])}")
                    elif src["path"].strip() == "":
                        errors.append(f"Source {idx}: 'path' cannot be empty")

                # optional: name
                if "name" in src and not isinstance(src["name"], str):
                    errors.append(f"Source {idx}: 'name' must be a string, got {type_name(src['name'])}")

                # optional: recursive
                if "recursive" in src and not isinstance(src["recursive"], bool):
                    errors.append(f"Source {idx}: 'recursive' must be a boolean, got {type_name(src['recursive'])}")

                # optional patterns: must be lists if present
                if "include_patterns" in src and not isinstance(src["include_patterns"], list):
                    errors.append(f"Source {idx}: 'include_patterns' must be a list, got {type_name(src['include_patterns'])}")
                if "exclude_patterns" in src and not isinstance(src["exclude_patterns"], list):
                    errors.append(f"Source {idx}: 'exclude_patterns' must be a list, got {type_name(src['exclude_patterns'])}")

    # Destination fields
    if isinstance(destination, dict):
        if "base_path" not in destination:
            errors.append("Missing required field: 'destination.base_path'")
        else:
            bp = destination["base_path"]
            if not isinstance(bp, str):
                errors.append(f"'destination.base_path' must be a string, got {type_name(bp)}")
            elif bp.strip() == "":
                errors.append("'destination.base_path' cannot be empty")

        if "create_timestamped_folders" in destination and not isinstance(destination["create_timestamped_folders"], bool):
            errors.append(f"'destination.create_timestamped_folders' must be a boolean, got {type_name(destination['create_timestamped_folders'])}")

        if "retention_days" in destination and not isinstance(destination["retention_days"], (int, float)):
            errors.append(f"'destination.retention_days' must be a number, got {type_name(destination['retention_days'])}")

    # Options fields
    if isinstance(options, dict):
        if "verify_backups" in options and not isinstance(options["verify_backups"], bool):
            errors.append(f"'options.verify_backups' must be a boolean, got {type_name(options['verify_backups'])}")
        if "max_file_size_mb" in options and not isinstance(options["max_file_size_mb"], (int, float)):
            errors.append(f"'options.max_file_size_mb' must be a number, got {type_name(options['max_file_size_mb'])}")

    return len(errors) == 0, errors

# --------------------------------
# Part 4: Function: simulate_backup
# --------------------------------

def _fake_name_from_pattern(source_name: str, pattern: str, i: int, when: str) -> str:
    """Create a realistic filename from a glob-like pattern."""
    pattern = (pattern or "*").lower()
    date = when.split("T")[0]  # YYYY-MM-DD

    # Heuristics by extension / keyword
    if pattern.endswith(".log") or "*.log" in pattern:
        base = source_name.lower().replace(" ", "_")
        variants = [
            f"{base}_{date}.log",
            f"access_{date}.log",
            f"events_{date}.log",
            f"{base}.log",
            f"{base}_{i}.log"
        ]
        return random.choice(variants)
    if pattern.endswith(".txt") or "*.txt" in pattern:
        return random.choice([f"readme_{i}.txt", f"summary_{date}.txt", f"notes_{i}.txt"])
    if pattern.endswith(".json") or "*.json" in pattern:
        return random.choice([f"alerts_{date}.json", f"events_{i}.json", f"batch_{i:03d}.json"])
    if "auth.log" in pattern:
        return random.choice(["auth.log", "auth.log.1", "auth.log.2", f"auth_{date}.log"])
    if "*.gz" in pattern:
        return random.choice([f"{source_name.lower().replace(' ','_')}_{i}.log.gz", f"archive_{date}.gz"])
    # Default
    return f"{source_name.lower().replace(' ','_')}_{i}.dat"

def simulate_backup(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """
    DRY-RUN: Generate FAKE operations. No filesystem I/O.
    - Creates 5–15 fake files per source
    - File sizes: 1–100 MB (or capped by options.max_file_size_mb)
    - Shows source → destination mapping
    """
    meta = cfg.get("metadata", {})
    plan_name = meta.get("plan_name") or cfg.get("plan_name") or "Unnamed Plan"
    dest = cfg.get("destination", {})
    opts = cfg.get("options", {}) or {}

    timestamp = iso_now()
    ts_folder = timestamp.replace(":", "").replace("-", "").replace("T", "_")
    base_path = dest.get("base_path", "/backups")
    use_ts = bool(dest.get("create_timestamped_folders", False))

    max_mb = float(opts.get("max_file_size_mb", 100))
    max_mb = clamp(max_mb, 1.0, 1000.0)  # sane cap

    operations = []
    total_files = 0
    total_size_mb = 0.0

    for src in cfg.get("sources", []):
        src_name = src.get("name") or src.get("path", "unknown")
        include = src.get("include_patterns") or ["*"]
        exclude = src.get("exclude_patterns") or []  # not applied in fake mode, but kept for show

        # Files per source
        n_files = random.randint(5, 15)
        files = []
        for i in range(1, n_files + 1):
            pat = random.choice(include)
            fname = _fake_name_from_pattern(src_name, pat, i, timestamp)
            size = round(random.uniform(1.0, max_mb), 1)  # MB
            files.append({"name": fname, "size_mb": size})

        src_total = round(sum(f["size_mb"] for f in files), 1)
        total_files += len(files)
        total_size_mb += src_total

        dest_path = f"{base_path}/{plan_name.replace(' ', '_')}/{src_name.replace(' ', '_')}"
        if use_ts:
            dest_path = f"{dest_path}/{ts_folder}"

        operations.append({
            "source_name": src_name,
            "source_path": src.get("path", ""),
            "destination_path": dest_path,
            "files": files,
            "source_summary": {
                "count": len(files),
                "total_size_mb": src_total
            },
            "patterns_used": {
                "include": include,
                "exclude": exclude
            }
        })

    report = {
        "plan_name": plan_name,
        "mode": "DRY-RUN",
        "timestamp": timestamp,
        "summary": {
            "total_sources": len(cfg.get("sources", [])),
            "total_files": total_files,
            "total_size_mb": round(total_size_mb, 1)
        },
        "operations": operations
    }
    return report

# --------------------------------
# Part 3: Function: generate_report
# --------------------------------

def generate_report(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"Backup Plan Report — {report['plan_name']}")
    lines.append(f"Mode: {report['mode']}   Time: {report['timestamp']}")
    lines.append("-" * 70)
    s = report["summary"]
    lines.append(f"Sources: {s['total_sources']} | Files: {s['total_files']} | Size: {s['total_size_mb']} MB")
    lines.append("")

    for op in report["operations"]:
        lines.append(f"[{op['source_name']}]")
        lines.append(f"  From: {op['source_path']}")
        lines.append(f"  To:   {op['destination_path']}")
        lines.append(f"  Files: {op['source_summary']['count']}  |  Size: {op['source_summary']['total_size_mb']} MB")
        lines.append(f"  Include: {op['patterns_used']['include']}")
        if op['patterns_used']['exclude']:
            lines.append(f"  Exclude: {op['patterns_used']['exclude']}")
        # Show up to 5 sample files
        sample = op["files"][:5]
        if sample:
            lines.append("  Sample files:")
            for f in sample:
                lines.append(f"    • {f['name']}  ({f['size_mb']} MB)")
        lines.append("")

    return "\n".join(lines)

# -----------------------------
# Part 3: Function: main
# -----------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Simple backup planner (DRY-RUN simulation only)")
    parser.add_argument("--config", required=True, help="Path to JSON configuration file")
    parser.add_argument("--dry-run", action="store_true", help="Simulate only (default behavior)")
    parser.add_argument("--json-out", help="Optional path to write JSON report")
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    if cfg is None:
        return 1

    is_valid, val_errors = validate_config(cfg)
    if not is_valid:
        print(f"Validation failed with {len(val_errors)} error(s):")
        for e in val_errors:
            print(f" - {e}")
        return 2

    report = simulate_backup(cfg)
    print(generate_report(report))

    if args.json_out:
        try:
            with open(args.json_out, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            print(f"(JSON written to {args.json_out})")
        except Exception as ex:
            print(f"Warning: could not write JSON report: {ex}")

    if not args.dry_run:
        print("Note: This app only supports DRY-RUN simulation (no real file operations).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())