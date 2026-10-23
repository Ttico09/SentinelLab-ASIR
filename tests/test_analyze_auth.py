import unittest

from scripts.analyze_auth import analyze_lines, parse_event


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

    def test_parser_preserves_password_method(self):
        event = parse_event(entry(0))

        self.assertIsNotNone(event)
        self.assertEqual(event["auth_method"], "password")
        self.assertEqual(event["result"], "failed")

    def test_parser_rejects_invalid_ip(self):
        event = parse_event(entry(0, ip="999.0.2.44"))

        self.assertIsNone(event)

    def test_parser_accepts_publickey(self):
        line = (
            "2026-10-15T08:10:00+00:00 lab sshd[235]: "
            "Accepted publickey for alumno from 192.0.2.44 "
            "port 42751 ssh2: ED25519 SHA256:ejemplo"
        )

        event = parse_event(line)

        self.assertIsNotNone(event)
        self.assertEqual(event["result"], "accepted")
        self.assertEqual(event["user"], "alumno")
        self.assertEqual(event["ip"], "192.0.2.44")
        self.assertEqual(event["auth_method"], "publickey")

    def test_parser_normalizes_ipv6(self):
        event = parse_event(
            entry(0, ip="2001:0db8:0000:0000:0000:0000:0000:0044")
        )

        self.assertIsNotNone(event)
        self.assertEqual(event["ip"], "2001:db8::44")

    def test_parser_rejects_invalid_date(self):
        line = entry(0).replace("2026-10-15", "2026-02-30")

        self.assertIsNone(parse_event(line))

    def test_parser_rejects_timestamp_without_timezone(self):
        line = entry(0).replace("+00:00", "")

        self.assertIsNone(parse_event(line))

    def test_reports_parsing_counts(self):
        lines = [
            entry(0),
            entry(1, ip="999.0.2.44"),
            (
                "2026-10-15T08:02:00+00:00 lab sshd[123]: "
                "Connection closed by 192.0.2.44 port 42751"
            ),
            "2026-10-15T08:03:00+00:00 lab cron[2]: tarea ejecutada",
        ]

        result = analyze_lines(lines)

        self.assertIn("parsing", result)
        self.assertEqual(
            result["parsing"],
            {
                "total_lines": 4,
                "parsed_events": 1,
                "non_ssh_lines": 1,
                "unparsed_ssh_lines": 2,
            },
        )
        self.assertEqual(result["summary"]["events"], 1)


if __name__ == '__main__':
    unittest.main()
