from datetime import datetime
from enum import Enum


class DriftType(str, Enum):
    MISSING = "MISSING"
    EXTRA = "EXTRA"
    CHANGED = "CHANGED"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DriftResult:
    def __init__(self, path, drift_type, baseline_value, current_value):
        self.path = path or "root"
        self.drift_type = DriftType(drift_type)
        self.baseline_value = baseline_value
        self.current_value = current_value
        self.timestamp = datetime.utcnow().isoformat()
        self.severity = self._calculate_severity()

    def _calculate_severity(self):
        if self.drift_type == DriftType.MISSING:
            return Severity.CRITICAL
        if self.drift_type == DriftType.CHANGED:
            return Severity.HIGH
        if self.drift_type == DriftType.EXTRA:
            return Severity.MEDIUM
        return Severity.LOW

    def is_critical(self):
        return self.severity == Severity.CRITICAL

    def to_dict(self):
        return {
            "path": self.path,
            "drift_type": self.drift_type.value,
            "severity": self.severity.value,
            "baseline_value": self.baseline_value,
            "current_value": self.current_value,
            "timestamp": self.timestamp,
        }

    def __str__(self):
        return (
            f"[{self.severity.value}] {self.drift_type.value} at '{self.path}'\n"
            f"  Baseline: {self.baseline_value}\n"
            f"  Current : {self.current_value}"
        )