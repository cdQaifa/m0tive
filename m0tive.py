#!/usr/bin/env python3
"""
m0tive - Motivational automation bot

How to run:
  python3 m0tive.py

Dependencies:
  - Python 3.10+

Run in background (examples):
  nohup python3 m0tive.py > /dev/null 2>&1 &
  python3 m0tive.py --daemon
"""

from __future__ import annotations

import argparse
import os
import random
import signal
import sys
import time
from datetime import datetime
from typing import List

BOT_NAME = "m0tive"
INTERVAL_MINUTES = 60
LOG_FILE = "m0tive.log"

MESSAGES: List[str] = [
    "Discipline creates freedom.",
    "Consistency beats intensity.",
    "Ship small, ship often.",
    "Focus on the next commit, not the whole mountain.",
    "Progress is the product of patience.",
    "Small wins build unstoppable momentum.",
    "Your future code depends on today’s effort.",
    "Write it, test it, trust it.",
    "Daily practice turns ideas into impact.",
    "One focused hour beats a distracted day.",
    "Your habits are your roadmap.",
    "Build systems, not excuses.",
    "Clean code starts with clear thinking.",
    "Consistency is the real productivity hack.",
    "Great software is built one disciplined day at a time.",
    "Momentum is earned, not given.",
    "Dreams require deadlines.",
    "Show up, even when it’s hard.",
    "The long game always wins.",
    "Turn setbacks into setups.",
    "Push one more commit.",
    "A calm mind writes better code.",
    "Structure fuels creativity.",
    "Today’s effort is tomorrow’s expertise.",
    "Be consistent, then be relentless.",
    "Ship with purpose.",
    "Discipline is a form of self-respect.",
    "Your codebase grows with your discipline.",
    "Master the boring, earn the brilliant.",
    "Build the habit, build the future.",
    "Think in milestones, act in minutes.",
    "Clarity comes from doing.",
    "Refactor your habits, not just your code.",
    "Success is scheduled, not spontaneous.",
    "Deep work creates deep results.",
    "Consistency compounds into mastery.",
    "Every hour invested is a brick in your legacy.",
    "Make progress visible, then make it steady.",
    "One bug fixed is one step forward.",
    "Keep your promises to yourself.",
    "Long-term goals require short-term discipline.",
    "Stay sharp; excellence is a habit.",
    "Build today what your future self will thank you for.",
    "Write code with intent.",
    "The grind is where growth lives.",
    "Your schedule is your strategy.",
    "Consistency turns vision into reality.",
    "Greatness is a series of small, smart choices.",
    "Aim for progress, not perfection.",
    "Discipline turns talent into results.",
    "Keep your focus; your goals are waiting.",
    "Success is built in quiet hours.",
]

DYNAMIC_TEMPLATES = [
    "Stay {adjective} and keep {verb} toward your {goal}.",
    "{action} today so your {goal} grows tomorrow.",
    "{adjective} focus makes {goal} inevitable.",
    "Keep {verb}; your {goal} is closer than you think.",
]

DYNAMIC_WORDS = {
    "adjective": ["disciplined", "steady", "focused", "consistent", "relentless"],
    "verb": ["building", "iterating", "shipping", "learning", "improving"],
    "goal": ["mastery", "success", "momentum", "career", "long-term vision"],
    "action": ["Invest an hour", "Write one feature", "Fix one bug", "Review your roadmap"],
}


def generate_dynamic_message() -> str:
    template = random.choice(DYNAMIC_TEMPLATES)
    return template.format(
        adjective=random.choice(DYNAMIC_WORDS["adjective"]),
        verb=random.choice(DYNAMIC_WORDS["verb"]),
        goal=random.choice(DYNAMIC_WORDS["goal"]),
        action=random.choice(DYNAMIC_WORDS["action"]),
    )


def select_message(use_dynamic: bool = True) -> str:
    if use_dynamic and random.random() < 0.25:
        return generate_dynamic_message()
    return random.choice(MESSAGES)


def log_message(message: str, log_path: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {BOT_NAME}: {message}\n"
    try:
        with open(log_path, "a", encoding="utf-8") as handle:
            handle.write(line)
    except OSError:
        print(f"[{BOT_NAME}] Failed to write log file.", file=sys.stderr)


def terminal_output(message: str) -> None:
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"[{BOT_NAME}] [{current_time}] {message}")


def send_notification(message: str) -> None:
    if sys.platform.startswith("linux") and shutil_which("notify-send"):
        os.system(f"notify-send '{BOT_NAME}' '{message}'")


def run_cycle(log_path: str, use_notifications: bool, use_dynamic: bool) -> None:
    message = select_message(use_dynamic=use_dynamic)
    terminal_output(message)
    log_message(message, log_path)
    if use_notifications:
        send_notification(message)


def scheduler_loop(interval_minutes: int, log_path: str, use_notifications: bool, use_dynamic: bool) -> None:
    interval_seconds = max(1, interval_minutes * 60)
    next_run = time.time()
    while True:
        try:
            now = time.time()
            if now >= next_run:
                run_cycle(log_path, use_notifications, use_dynamic)
                next_run = now + interval_seconds
            time.sleep(1)
        except Exception as exc:
            print(f"[{BOT_NAME}] Error: {exc}", file=sys.stderr)
            time.sleep(5)


def daemonize() -> None:
    if os.name != "posix":
        return
    try:
        pid = os.fork()
        if pid > 0:
            os._exit(0)
    except OSError:
        return

    os.setsid()

    try:
        pid = os.fork()
        if pid > 0:
            os._exit(0)
    except OSError:
        return

    sys.stdout.flush()
    sys.stderr.flush()
    with open("/dev/null", "r") as dev_null:
        os.dup2(dev_null.fileno(), sys.stdin.fileno())
    with open("/dev/null", "a+") as dev_null:
        os.dup2(dev_null.fileno(), sys.stdout.fileno())
        os.dup2(dev_null.fileno(), sys.stderr.fileno())


def shutdown_handler(signum, frame) -> None:
    print(f"[{BOT_NAME}] Shutting down.")
    sys.exit(0)


def shutil_which(binary: str) -> str | None:
    for path in os.environ.get("PATH", "").split(os.pathsep):
        candidate = os.path.join(path, binary)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="m0tive motivational bot")
    parser.add_argument("--interval", type=int, default=INTERVAL_MINUTES, help="Interval in minutes")
    parser.add_argument("--log-file", default=LOG_FILE, help="Log file path")
    parser.add_argument("--no-dynamic", action="store_true", help="Disable dynamic messages")
    parser.add_argument("--notify", action="store_true", help="Enable desktop notifications (Linux)")
    parser.add_argument("--daemon", action="store_true", help="Run in background (POSIX only)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.daemon:
        daemonize()

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    scheduler_loop(
        interval_minutes=args.interval,
        log_path=args.log_file,
        use_notifications=args.notify,
        use_dynamic=not args.no_dynamic,
    )


if __name__ == "__main__":
    main()
