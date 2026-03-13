
from drift_checker.engine import DriftEngine

def main():
    engine = DriftEngine('baseline.json', 'current.json')
    engine.run()

if __name__ == '__main__':
    main()
