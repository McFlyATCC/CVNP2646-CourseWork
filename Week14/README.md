# 📘 Threat Log Normalizer – Capstone MVP (Week 14)

## Project Overview

Threat Log Normalizer is a Python-based security tool that ingests raw threat event logs, normalizes them into structured objects, evaluates risk, and generates a summarized security report via a command-line interface (CLI).

This MVP focuses on **clarity, correctness, and defensive programming** rather than full production scale.

---

## Problem Statement

Security logs are often inconsistent, incomplete, or malformed. This makes automated analysis and reporting difficult.

The goal of this project is to:

- Normalize raw threat log input
- Apply basic risk scoring
- Identify critical security events
- Generate a summarized, machine-readable report

---

## System Architecture

```
┌──────────────┐
│ Raw JSON Log │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ ThreatEvent       │
│ - validate fields │
│ - calculate risk  │
│ - critical flag   │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ ThreatReport      │
│ - aggregation     │
│ - statistics      │
│ - JSON output     │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Report JSON File  │
└──────────────────┘
```

---

## Data Model

### ThreatEvent Fields

| Field | Type | Description |
|------|-----|-------------|
| source_ip | string | Originating IP address |
| event_type | string | Type of threat event |
| timestamp | datetime | Time of event |
| severity | integer (1–10) | Reported severity |

### Derived Attributes

| Attribute | Description |
|---------|-------------|
| risk_score | Calculated risk value |
| critical | Boolean flag indicating high risk |

---

## Risk Calculation Logic

### Event Type Weighting

| Event Type | Risk Bonus |
|----------|------------|
| DATA_EXFILTRATION | +7 |
| MALWARE_DETECTED | +5 |
| BRUTE_FORCE | +4 |
| Other | +0 |

### Formula

```
risk_score = severity + event_type_bonus
```

Events with a risk score **≥ 10** are flagged as **critical**.

---

## CLI Usage

### Basic Command

```bash
python main.py --input events.json --report
```

### Available Arguments

| Argument | Purpose |
|--------|--------|
| --input | Path to input JSON log file |
| --report | Generate threat summary report |
| --output | Output report filename |
| --min-severity | Filter out low-severity events |
| --critical-only | Include only critical events |
| --strict | Fail on malformed input |
| --verbose | Enable debug output |

---

## Sample Report Output (Excerpt)

```json
{
  "summary": {
    "total_events": 12,
    "critical_events": 4,
    "average_risk_score": 8.5
  }
}
```

---

## Error Handling Strategy

| Scenario | Behavior |
|--------|---------|
| Invalid timestamp | Event skipped with warning |
| Missing required field | Logged and skipped |
| Invalid severity type | Rejected |
| Invalid IP format | Logged but ingested |

Strict parsing can be enforced using the `--strict` flag.

---

## Project Status

✅ Week 14 MVP Complete  
⬜ Dashboard (Future)  
⬜ Persistent storage (Future)  

---

## How to Run

```bash
pip install -r requirements.txt
python main.py --input test_events.json --report
```

---

# 🧪 Checkpoint Write‑Up (Week 14)

## Objective

The goal of the Week 14 checkpoint was to implement a **minimum viable product** demonstrating object-oriented design, log normalization, basic analytics, and CLI interaction.

---

## Implemented Features

| Component | Status |
|----------|--------|
| ThreatEvent class | ✅ |
| Risk scoring logic | ✅ |
| Critical event detection | ✅ |
| Log normalization | ✅ |
| CLI ingestion | ✅ |
| Report generation | ✅ |
| Error handling | ✅ |

---

## Design Decisions

### Object-Oriented Design

Each threat event is modeled as a `ThreatEvent` object, allowing risk logic and validation to be encapsulated within the object rather than scattered across the application.

### Simple Risk Model

A rule-based risk scoring approach was chosen instead of machine learning to ensure deterministic behavior and limit scope.

### Defensive Parsing

Security logs often contain malformed data. The application defaults to skipping invalid entries while logging warnings, with an option to fail immediately using `--strict`.

---

## Testing Strategy

### Test Dataset Breakdown

| Category | Count |
|--------|------|
| Valid events | 11 |
| Malformed events | 5 |
| Edge cases | 4 |

Malformed inputs include invalid timestamps, missing fields, incorrect data types, and out-of-range severity values.

---

## Known Limitations

| Limitation | Reason |
|----------|--------|
| No database | Not required for MVP |
| No GUI | CLI-focused scope |
| Static risk rules | Configurable in future versions |

---

## Learning Outcomes

- Practical object-oriented programming
- CLI application development
- Defensive programming
- Threat data normalization
- Basic security analytics

---

## Planned Enhancements

```
[ ] Unit tests (pytest)
[ ] CSV export
[ ] Configurable risk rules
[ ] Docker container
```

---

✅ **All Week 14 requirements satisfied with a functional MVP demonstrating core security tool behavior.**
