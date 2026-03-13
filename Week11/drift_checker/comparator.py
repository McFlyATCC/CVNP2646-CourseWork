
from .models import DriftResult, DriftType
from .normalizer import ValueNormalizer

class ConfigComparator:
    def compare(self, baseline, current, path=""):
        results = []

        if isinstance(baseline, dict) and '__parse_error__' in baseline:
            return [DriftResult(path, DriftType.CHANGED, 'Valid JSON', baseline)]

        if isinstance(current, dict) and '__parse_error__' in current:
            return [DriftResult(path, DriftType.CHANGED, 'Valid JSON', current)]

        if isinstance(baseline, dict) and isinstance(current, dict):
            for key in baseline:
                new_path = f"{path}.{key}" if path else key
                if key not in current:
                    results.append(DriftResult(new_path, DriftType.MISSING, baseline[key], None))
                else:
                    results.extend(self.compare(baseline[key], current[key], new_path))

            for key in current:
                if key not in baseline:
                    new_path = f"{path}.{key}" if path else key
                    results.append(DriftResult(new_path, DriftType.EXTRA, None, current[key]))

        elif isinstance(baseline, list) and isinstance(current, list):
            min_len = min(len(baseline), len(current))
            for i in range(min_len):
                results.extend(self.compare(baseline[i], current[i], f"{path}[{i}]"))

            for i in range(min_len, len(baseline)):
                results.append(DriftResult(f"{path}[{i}]", DriftType.MISSING, baseline[i], None))

            for i in range(min_len, len(current)):
                results.append(DriftResult(f"{path}[{i}]", DriftType.EXTRA, None, current[i]))
        else:
            base = ValueNormalizer.normalize(baseline)
            curr = ValueNormalizer.normalize(current)
            if base != curr:
                results.append(DriftResult(path, DriftType.CHANGED, baseline, current))

        return results
