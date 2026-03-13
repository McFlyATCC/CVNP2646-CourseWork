
import json

class ConfigLoader:
    @staticmethod
    def load(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            return {"__parse_error__": f"Invalid JSON: {e}"}
        except Exception as e:
            return {"__file_error__": str(e)}
