#!/usr/bin/env python3
"""Seed Uptime Kuma monitors from monitoring/uptime-kuma/monitors.yaml."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import yaml

try:
    from uptime_kuma_api import MonitorType, UptimeKumaApi
except ImportError:
    print("Missing dependency. Install with:", file=sys.stderr)
    print("  pip install -r scripts/requirements-uptime-kuma.txt", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
MONITORS_FILE = ROOT / "monitoring" / "uptime-kuma" / "monitors.yaml"

DEFAULT_URL = "http://localhost:3002"
DEFAULT_INTERVAL = 60


def load_monitors() -> list[dict]:
    with MONITORS_FILE.open() as f:
        data = yaml.safe_load(f)
    return data.get("monitors", [])


def main() -> int:
    base_url = os.environ.get("UPTIME_KUMA_URL", DEFAULT_URL)
    username = os.environ.get("UPTIME_KUMA_USERNAME")
    password = os.environ.get("UPTIME_KUMA_PASSWORD")

    if not username or not password:
        print(
            "Set UPTIME_KUMA_USERNAME and UPTIME_KUMA_PASSWORD "
            "(the account you created at first login).",
            file=sys.stderr,
        )
        return 1

    desired = load_monitors()
    if not desired:
        print(f"No monitors defined in {MONITORS_FILE}", file=sys.stderr)
        return 1

    with UptimeKumaApi(base_url) as api:
        api.login(username, password)
        existing = {m["name"]: m for m in api.get_monitors()}

        added = 0
        skipped = 0
        for monitor in desired:
            name = monitor["name"]
            if name in existing:
                print(f"skip  {name} (already exists)")
                skipped += 1
                continue

            result = api.add_monitor(
                type=MonitorType.HTTP,
                name=name,
                url=monitor["url"],
                interval=monitor.get("interval", DEFAULT_INTERVAL),
            )
            print(f"add   {name} -> {monitor['url']} (id={result.get('monitorId')})")
            added += 1

    print(f"\nDone: {added} added, {skipped} skipped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
