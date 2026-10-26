#!/usr/bin/env python3
"""Analiza registros SSH de un laboratorio propio y genera alertas defensivas.

Compatible con Python >=3.10. No utiliza dependencias externas.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from ipaddress import ip_address
import json
from pathlib import Path
import re

LINE = re.compile(
    r"^(?P<time>\S+)\s+.+?sshd(?:-session)?\[\d+\]:\s+(?P<message>.+)$"
    )
AUTH = re.compile(
    r"^(?P<action>Failed|Accepted) "
    r"(?P<method>password|publickey) for "
    r"(?:invalid user )?(?P<user>\S+) "
    r"from (?P<ip>\S+) port \d+ ssh2"
    r"(?:: (?P<key_details>.+))?$"
)
SSH_PROCESS = re.compile(r"(?:^|\s)sshd(?:-session)?\[\d+\]:")

def parse_event(line):
    """Devuelve un evento SSH normalizado o None si la línea no coincide."""
    match = LINE.match(line.strip())
    if not match:
        return None
    auth = AUTH.match(match.group('message'))
    if not auth:
        return None
    try:
        timestamp = datetime.fromisoformat(match.group('time').replace('Z', '+00:00'))
        if timestamp.tzinfo is None:
            return None
        ip = str(ip_address(auth.group('ip')))
    except ValueError:
        return None
    return {
        "timestamp": timestamp,
        "ip": ip,
        "user": auth.group("user"),
        "result": (
            "failed" if auth.group("action") == "Failed" else "accepted"
        ),
        "auth_method": auth.group("method"),
    }


def analyze_lines(lines, threshold=5, window_minutes=15, success_threshold=3):
    if threshold < 1 or window_minutes < 1 or success_threshold < 1:
        raise ValueError(
            "threshold, window_minutes y success_threshold "
            "deben ser mayores que cero"
        )

    events = []
    parsing = {
        "total_lines": 0,
        "parsed_events": 0,
        "non_ssh_lines": 0,
        "unparsed_ssh_lines": 0,
    }

    for line in lines:
        parsing["total_lines"] += 1
        event = parse_event(line)

        if event is not None:
            events.append(event)
            parsing["parsed_events"] += 1
        elif SSH_PROCESS.search(line):
            parsing["unparsed_ssh_lines"] += 1
        else:
            parsing["non_ssh_lines"] += 1

    events.sort(key=lambda event: event["timestamp"])
    failed_by_ip = defaultdict(list)
    failed_by_account = defaultdict(list)
    counted_ips = set()
    alerts = []
    totals = Counter()

    for event in events:
        ip, time = event['ip'], event['timestamp']
        account = (ip, event["user"])
        recent_account = [
            timestamp
            for timestamp in failed_by_account[account]
            if timedelta(0) <= time - timestamp
            <= timedelta(minutes=window_minutes)
        ]
        totals[event['result']] += 1
        recent = [t for t in failed_by_ip[ip] if timedelta(0) <= time - t <= timedelta(minutes=window_minutes)]

        if not recent:
            counted_ips.discard(ip)

        if event['result'] == 'failed':
            recent.append(time)
            recent_account.append(time)
            if len(recent) >= threshold and ip not in counted_ips:
                alerts.append({'type': 'repeated_ssh_failures', 'severity': 'high', 'ip': ip,
                               'timestamp': time.isoformat(), 'failed_attempts': len(recent),
                               'detail': f'{len(recent)} intentos fallidos en {window_minutes} minutos'})
                counted_ips.add(ip)
        elif len(recent_account) >= success_threshold:
            alerts.append({
                "type": "ssh_success_after_failures",
                "severity": "medium",
                "ip": ip,
                "user": event["user"],
                "timestamp": time.isoformat(),
                "failed_attempts": len(recent_account),
                "detail": (
                    "Autenticación correcta tras varios fallos recientes "
                    "para la misma IP y usuario"
                ),
            })
            
        if event["result"] == "accepted":
            recent_account = []

        failed_by_ip[ip] = recent
        failed_by_account[account] = recent_account

    top_ips = Counter(event['ip'] for event in events if event['result'] == 'failed')
    return {'project': 'SentinelLab ASIR', 'source': 'SSH authentication logs', 'parsing': parsing,
            'summary': {'events': len(events), 'failed': totals['failed'],
                        'accepted': totals['accepted'], 'alerts': len(alerts)},
            'top_failed_ips': [{'ip': ip, 'count': count} for ip, count in top_ips.most_common(10)],
            'alerts': alerts}


def main():
    parser = argparse.ArgumentParser(description='Analizador defensivo de registros SSH')
    parser.add_argument('--input', type=Path, default=Path('data/sample_auth.log'))
    parser.add_argument('--output', type=Path, default=Path('docs/dashboard/report.json'))
    parser.add_argument('--threshold', type=int, default=5)
    parser.add_argument('--window-minutes', type=int, default=15)
    parser.add_argument(
        "--success-threshold",
        type=int,
        default=3,
        help="Fallos previos de la misma IP y usuario para alertar tras un éxito",
    )
    args = parser.parse_args()
    report = analyze_lines(
        args.input.read_text(encoding="utf-8").splitlines(),
        threshold=args.threshold,
        window_minutes=args.window_minutes,
        success_threshold=args.success_threshold,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Analizados {report['summary']['events']} eventos. Alertas: {report['summary']['alerts']}. Guardado en {args.output}")


if __name__ == '__main__':
    main()
