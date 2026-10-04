#!/usr/bin/env python3
"""
Wait until a random moment between 12:00 and 15:00 Europe/Madrid, then play salsa.
Designed to be started once per day by launchd (see install script).
"""

from __future__ import annotations

import random
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

MADRID = ZoneInfo("Europe/Madrid")
WINDOW_START_HOUR = 12
WINDOW_HOURS = 3

ROOT = Path(__file__).resolve().parent.parent
PLAY_SCRIPT = ROOT / "scripts" / "play_salsa.py"


def random_target_today(now: datetime) -> datetime:
    day_start = now.replace(
        hour=WINDOW_START_HOUR, minute=0, second=0, microsecond=0
    )
    offset_seconds = random.randint(0, WINDOW_HOURS * 3600 - 1)
    return day_start + timedelta(seconds=offset_seconds)


def main() -> int:
    now = datetime.now(MADRID)
    window_end = now.replace(
        hour=WINDOW_START_HOUR + WINDOW_HOURS, minute=0, second=0, microsecond=0
    )

    if now >= window_end:
        print(
            f"[{now.isoformat()}] Practice window already closed (after 15:00 Madrid).",
            flush=True,
        )
        return 0

    target = random_target_today(now)
    if target < now:
        # launchd started late in the window — pick a random time from now until 15:00.
        remaining = int((window_end - now).total_seconds())
        if remaining <= 0:
            return 0
        target = now + timedelta(seconds=random.randint(0, remaining - 1))

    wait_seconds = max(0, (target - now).total_seconds())
    print(
        f"[{now.isoformat()}] Next practice at {target.isoformat()} "
        f"(sleep {wait_seconds:.0f}s)",
        flush=True,
    )
    time.sleep(wait_seconds)

    print(f"[{datetime.now(MADRID).isoformat()}] Starting salsa practice.", flush=True)
    return subprocess.call([sys.executable, str(PLAY_SCRIPT)])


if __name__ == "__main__":
    raise SystemExit(main())
