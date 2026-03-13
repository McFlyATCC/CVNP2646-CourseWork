
class ValueNormalizer:
    @staticmethod
    def normalize(value):
        if isinstance(value, str):
            v = value.strip().lower()
            if v == 'true':
                return True
            if v == 'false':
                return False
            try:
                return int(value)
            except ValueError:
                try:
                    return float(value)
                except ValueError:
                    return value.strip()
        return value
