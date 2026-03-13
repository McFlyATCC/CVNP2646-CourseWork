
from .loader import ConfigLoader
from .comparator import ConfigComparator
from .reporter import DriftReporter

class DriftEngine:
    def __init__(self, baseline_path, current_path):
        self.baseline_path = baseline_path
        self.current_path = current_path
        self.comparator = ConfigComparator()

    def run(self):
        baseline = ConfigLoader.load(self.baseline_path)
        current = ConfigLoader.load(self.current_path)
        results = self.comparator.compare(baseline, current)
        DriftReporter.display(results)
        return results
