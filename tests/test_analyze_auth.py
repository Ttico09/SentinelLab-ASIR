import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from analyze_auth import analyze_lines, parse_event


def entry(when, action='Failed', ip='203.0.113.25'):
    return f'2026-10-15T08:{when:02d}:00+00:00 lab sshd[123]: {action} password for invalid user admin from {ip} port 52348 ssh2'


class TestSSHDetection(unittest.TestCase):
    def test_parser(self):
        event = parse_event(entry(0))
        self.assertEqual(event['ip'], '203.0.113.25')
        self.assertEqual(event['result'], 'failed')

    def test_detects_threshold(self):
        result = analyze_lines([entry(i) for i in range(5)])
        self.assertEqual(result['summary']['alerts'], 1)
        self.assertEqual(result['alerts'][0]['type'], 'repeated_ssh_failures')

    def test_ignores_sparse_attempts(self):
        result = analyze_lines([entry(0), entry(30), entry(40)])
        self.assertEqual(result['summary']['alerts'], 0)

    def test_success_after_failures(self):
        result = analyze_lines([entry(0), entry(1), entry(2), entry(3, 'Accepted')])
        self.assertEqual(result['alerts'][0]['type'], 'ssh_success_after_failures')

    def test_other_lines_ignored(self):
        result = analyze_lines(['esto no es syslog', entry(0)])
        self.assertEqual(result['summary']['events'], 1)

    def test_invalid_threshold(self):
        with self.assertRaises(ValueError):
            analyze_lines([], threshold=0)


if __name__ == '__main__':
    unittest.main()
