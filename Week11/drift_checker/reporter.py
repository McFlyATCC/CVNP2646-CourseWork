
class DriftReporter:
    @staticmethod
    def display(results):
        if not results:
            print('✅ No configuration drift detected.')
            return

        critical = [r for r in results if r.is_critical()]
        print('=' * 60)
        print('CONFIGURATION DRIFT REPORT')
        print('=' * 60)
        print(f'Total findings   : {len(results)}')
        print(f'Critical findings: {len(critical)}')
        print('-' * 60)
        for result in results:
            print(result)
            print('-' * 60)
        if critical:
            print('🚨 CRITICAL DRIFT DETECTED — IMMEDIATE ACTION REQUIRED')
