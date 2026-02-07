#!/usr/bin/env python3
"""
m0tive v2 - Motivational automation bot

Install dependencies:
  pip install rich schedule

Run:
  python3 m0tive.py

Run in background:
  nohup python3 m0tive.py &
"""

from __future__ import annotations

import argparse
import os
import random
import subprocess
import sys
import time
from collections import deque
from datetime import datetime
from typing import Deque, List

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
except ImportError:  # pragma: no cover - graceful fallback
    Console = None
    Panel = None
    Text = None

try:
    import schedule
except ImportError:  # pragma: no cover - graceful fallback
    schedule = None

BOT_NAME = "m0tive"
BOT_VERSION = "v2"
LANGUAGE = "en"
LOG_FILE = "m0tive_log.txt"
HISTORY_FILE = "m0tive_history.txt"
INTERVAL_MINUTES = 60

RECENT_HISTORY_LIMIT = 50
PROMO_MIN = 5
PROMO_MAX = 10

MESSAGES_EN: List[str] = [
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
    "Make time, then make progress.",
    "Protect your deep work like a treasure.",
    "Small steps, big outcomes.",
    "Build with intent, debug with patience.",
    "Future you needs present you to execute.",
    "Your roadmap starts with today’s action.",
    "Consistency is your competitive edge.",
    "A focused mind ships reliable code.",
    "Long-term wins come from short-term habits.",
    "Keep learning; your stack will thank you.",
    "Discipline is the quiet engine of success.",
    "Every refactor is a vote for quality.",
    "Make the hard thing your daily thing.",
    "One task completed beats ten postponed.",
    "Sharp focus makes great software.",
    "Commit to clarity, commit to growth.",
    "The best time to improve was yesterday; the next best is now.",
    "Consistency writes the story of your success.",
    "Plan the work, then work the plan.",
    "Keep your standards high and your excuses low.",
    "Your pace is your power when it’s steady.",
    "Progress loves a repeatable routine.",
    "Your skills are built in quiet hours.",
    "Stay curious; mastery follows.",
    "Stay sharp, stay humble, stay shipping.",
    "Quality is a daily decision.",
    "One hour of focus can change your week.",
    "Consistency makes the impossible inevitable.",
    "Build with patience, deliver with confidence.",
    "Execution is the shortcut.",
    "Prioritize the work that compounds.",
    "The long-term goal deserves today’s effort.",
    "Keep the loop tight: plan, code, test, improve.",
    "Discipline is the bridge from idea to impact.",
    "Focus turns ambition into outcomes.",
    "Protect your energy, invest your time.",
    "Your future is built in committed hours.",
    "Keep moving forward, one clean commit at a time.",
    "Success is the reward of steady effort.",
    "Stay consistent; your future depends on it.",
    "The habit is the strategy.",
    "Think long-term, act today.",
    "A little progress every day adds up.",
    "Be the developer who finishes.",
    "Clarity plus consistency equals momentum.",
    "Your legacy is built in repeatable actions.",
    "Let discipline do the heavy lifting.",
    "Keep your focus, keep your promise.",
    "Effort is the multiplier of talent.",
    "Steady execution beats bursts of intensity.",
    "Small improvements compound into mastery.",
    "Progress loves persistence.",
    "Make the next commit your best commit.",
    "Consistency is the quiet superpower.",
    "Respect the process; results will follow.",
    "Show up daily, then level up.",
    "Turn goals into routines.",
    "The future belongs to the consistent.",
    "Discipline today builds freedom tomorrow.",
]

MESSAGES_TR: List[str] = [
    "Disiplin özgürlük getirir.",
    "Tutarlılık, yoğunluğu yener.",
    "Küçük gönder, sık gönder.",
    "Dağın tamamına değil, sıradaki komite odaklan.",
    "İlerleme sabrın ürünüdür.",
    "Küçük kazanımlar durdurulamaz ivme yaratır.",
    "Gelecekteki kodun bugünkü çabana bağlı.",
    "Yaz, test et, güven.",
    "Günlük pratik fikirleri etkiye dönüştürür.",
    "Odaklı bir saat, dağınık bir günden iyidir.",
    "Alışkanlıkların yol haritandır.",
    "Bahaneler değil, sistemler kur.",
    "Temiz kod net düşünceyle başlar.",
    "Tutarlılık gerçek üretkenlik hilesidir.",
    "Harika yazılım disiplinli günlerle inşa edilir.",
    "İvme kazanılır, verilmez.",
    "Hayaller son tarih ister.",
    "Zor olsa da ortaya çık.",
    "Uzun oyun her zaman kazanır.",
    "Aksilikleri avantaja çevir.",
    "Bir commit daha at.",
    "Sakin zihin daha iyi kod yazar.",
    "Yapı yaratıcılığı besler.",
    "Bugünkü emek yarının uzmanlığıdır.",
    "Önce tutarlı ol, sonra kararlı.",
    "Amaçla gönder.",
    "Disiplin, özsaygının bir biçimidir.",
    "Kod tabanın disiplininle büyür.",
    "Sıkıcıyı ustalaş, parlaklığı kazan.",
    "Alışkanlığı kur, geleceği kur.",
    "Kilometre taşlarını düşün, dakikalarla hareket et.",
    "Netlik yaparak gelir.",
    "Sadece kodunu değil, alışkanlıklarını da refaktör et.",
    "Başarı planlanır, spontane olmaz.",
    "Derin çalışma derin sonuçlar doğurur.",
    "Tutarlılık ustalığa katlanır.",
    "Her saat mirasına bir tuğla ekler.",
    "İlerlemeyi görünür kıl, sonra istikrarlı kıl.",
    "Her hata düzeltmesi bir adımdır.",
    "Kendine verdiğin sözleri tut.",
    "Uzun vadeli hedefler kısa vadeli disiplin ister.",
    "Keskin kal; mükemmellik bir alışkanlıktır.",
    "Gelecekteki senin teşekkür edeceği şeyi bugün inşa et.",
    "Niyetle kod yaz.",
    "Büyüme yoğun çalışmada yaşar.",
    "Takvimin stratejindir.",
    "Tutarlılık vizyonu gerçeğe çevirir.",
    "Büyüklük, küçük ve akıllı seçimlerin serisidir.",
    "Mükemmellik değil ilerleme hedefle.",
    "Disiplin yeteneği sonuca dönüştürür.",
    "Odaklı kal; hedeflerin seni bekliyor.",
    "Başarı sessiz saatlerde inşa edilir.",
    "Önce zamanı ayır, sonra ilerle.",
    "Derin çalışmanı hazine gibi koru.",
    "Küçük adımlar büyük sonuçlar getirir.",
    "Niyetle inşa et, sabırla debug et.",
    "Gelecekteki sen bugünkü icrana ihtiyaç duyar.",
    "Yol haritan bugünün aksiyonuyla başlar.",
    "Tutarlılık rekabet avantajındır.",
    "Odaklı zihin güvenilir kod üretir.",
    "Uzun vadeli kazanımlar kısa vadeli alışkanlıklardan gelir.",
    "Öğrenmeye devam et; teknolojin teşekkür edecek.",
    "Disiplin başarının sessiz motorudur.",
    "Her refaktör kaliteye verilen bir oydur.",
    "Zoru günlük işin yap.",
    "Bitmiş bir iş, ertelenmiş on işten iyidir.",
    "Keskin odak harika yazılım yaratır.",
    "Netliğe bağlan, büyümeye bağlan.",
    "İyileştirmek için en iyi zaman dündü; ikinci en iyi zaman şimdi.",
    "Tutarlılık başarı hikayeni yazar.",
    "İşi planla, sonra planı uygula.",
    "Standartlarını yüksek, bahanelerini düşük tut.",
    "İstikrarlı olduğunda hızın gücündür.",
    "İlerleme tekrar eden rutinleri sever.",
    "Becerilerin sessiz saatlerde inşa edilir.",
    "Meraklı kal; ustalık gelir.",
    "Keskin kal, mütevazı kal, göndermeye devam et.",
    "Kalite günlük bir karardır.",
    "Odaklı bir saat haftanı değiştirebilir.",
    "Tutarlılık imkansızı kaçınılmaz kılar.",
    "Sabırla inşa et, güvenle teslim et.",
    "Uygulama en kestirme yoldur.",
    "Bileşik işlere öncelik ver.",
    "Uzun vadeli hedef bugünkü emeği hak eder.",
    "Döngüyü sıkı tut: planla, kodla, test et, geliştir.",
    "Disiplin fikri etkiye bağlayan köprüdür.",
    "Odak, hırsı sonuca çevirir.",
    "Enerjini koru, zamanını yatır.",
    "Geleceğin kararlı saatlerde inşa edilir.",
    "Bir sonraki commit ile ilerle.",
    "Başarı istikrarlı emeğin ödülüdür.",
    "Tutarlı kal; geleceğin buna bağlı.",
    "Alışkanlık stratejidir.",
    "Uzun vadeyi düşün, bugün harekete geç.",
    "Her gün biraz ilerleme birikir.",
    "Bitiren geliştirici ol.",
    "Netlik ve tutarlılık ivme yaratır.",
    "Mirasın tekrar eden aksiyonlarla kurulur.",
    "Ağır işi disipline bırak.",
    "Odağını koru, sözünü tut.",
    "Emek yeteneğin çarpanıdır.",
    "İstikrarlı uygulama, ani yoğunluktan güçlüdür.",
    "Küçük iyileştirmeler ustalığa katlanır.",
    "İlerleme ısrarı sever.",
    "Bir sonraki commit en iyi commitin olsun.",
    "Tutarlılık sessiz bir süper güçtür.",
    "Sürece saygı duy; sonuçlar gelir.",
    "Her gün görün, sonra seviye atla.",
    "Hedefleri rutine çevir.",
    "Gelecek tutarlı olanındır.",
    "Bugünün disiplini yarının özgürlüğünü kurar.",
]

TEMPLATES_EN = [
    "Every {action} you make builds your {future_object}.",
    "Stay {adjective} and keep {verb} toward your {goal}.",
    "{action} today so your {goal} grows tomorrow.",
    "{adjective} focus makes {goal} inevitable.",
    "Keep {verb}; your {goal} is closer than you think.",
    "Your {future_object} is shaped by {action} today.",
]

TEMPLATES_TR = [
    "Yaptığın her {action} senin {future_object} oluşturur.",
    "{adjective} kal ve {goal} için {verb}.",
    "Bugün {action}, yarın {goal} büyüsün.",
    "{adjective} odak {goal} kaçınılmaz kılar.",
    "{verb} etmeye devam et; {goal} sandığından yakın.",
    "{future_object} bugün yaptığın {action} ile şekillenir.",
]

WORDS_EN = {
    "action": ["effort", "commit", "decision", "practice", "hour of focus"],
    "future_object": ["legacy", "future", "career", "momentum", "mastery"],
    "adjective": ["disciplined", "steady", "focused", "consistent", "relentless"],
    "verb": ["building", "iterating", "shipping", "learning", "improving"],
    "goal": ["success", "growth", "momentum", "craft", "long-term vision"],
}

WORDS_TR = {
    "action": ["emek", "commit", "karar", "pratik", "odaklı bir saat"],
    "future_object": ["miras", "gelecek", "kariyer", "ivme", "ustalık"],
    "adjective": ["disiplinli", "istikrarlı", "odaklı", "tutarlı", "kararlı"],
    "verb": ["inşa etmeye", "geliştirmeye", "göndermeye", "öğrenmeye", "iyileştirmeye"],
    "goal": ["başarı", "büyüme", "ivme", "ustalık", "uzun vadeli vizyon"],
}

PROMOS_EN = [
    "Follow your progress. Build your legacy. GitHub: @cdQaifa",
    "Your code is your identity. GitHub: @cdQaifa",
    "Show your work, own your growth. GitHub: @cdQaifa",
]

PROMOS_TR = [
    "Gelişimini takip et. Mirasını inşa et. GitHub: @cdQaifa",
    "Kodun kimliğindir. GitHub: @cdQaifa",
    "Çalışmanı görünür kıl, büyümeni sahiplen. GitHub: @cdQaifa",
]


class HistoryManager:
    def __init__(self, path: str, limit: int) -> None:
        self.path = path
        self.limit = limit
        self.recent: Deque[str] = deque(maxlen=limit)

    def load(self) -> None:
        try:
            if not os.path.exists(self.path):
                return
            with open(self.path, "r", encoding="utf-8") as handle:
                for line in handle:
                    message = line.strip()
                    if message:
                        self.recent.append(message)
        except OSError:
            pass

    def save(self, message: str) -> None:
        try:
            with open(self.path, "a", encoding="utf-8") as handle:
                handle.write(message + "\n")
        except OSError:
            pass

    def is_recent(self, message: str) -> bool:
        return message in self.recent

    def remember(self, message: str) -> None:
        self.recent.append(message)


def generate_dynamic_message(language: str) -> str:
    templates = TEMPLATES_EN if language == "en" else TEMPLATES_TR
    words = WORDS_EN if language == "en" else WORDS_TR
    template = random.choice(templates)
    return template.format(
        action=random.choice(words["action"]),
        future_object=random.choice(words["future_object"]),
        adjective=random.choice(words["adjective"]),
        verb=random.choice(words["verb"]),
        goal=random.choice(words["goal"]),
    )


def select_language() -> str:
    if LANGUAGE in {"en", "tr"}:
        return LANGUAGE
    return random.choice(["en", "tr"])


def should_promote(counter: int) -> bool:
    threshold = random.randint(PROMO_MIN, PROMO_MAX)
    return counter >= threshold


def get_base_messages(language: str) -> List[str]:
    return MESSAGES_EN if language == "en" else MESSAGES_TR


def get_promos(language: str) -> List[str]:
    return PROMOS_EN if language == "en" else PROMOS_TR


def generate_message(history: HistoryManager, counter: int) -> str:
    language = select_language()
    base_messages = get_base_messages(language)
    dynamic_message = generate_dynamic_message(language)

    candidate_pool = base_messages + [dynamic_message]

    if should_promote(counter):
        candidate_pool.append(random.choice(get_promos(language)))

    random.shuffle(candidate_pool)

    for candidate in candidate_pool:
        if not history.is_recent(candidate):
            history.remember(candidate)
            return candidate

    fallback = random.choice(candidate_pool)
    history.remember(fallback)
    return fallback


def save_log(message: str, log_path: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{BOT_NAME}] {message}\n"
    try:
        with open(log_path, "a", encoding="utf-8") as handle:
            handle.write(line)
    except OSError:
        print(f"[{BOT_NAME}] Log write failed.", file=sys.stderr)


def display_terminal_ui(message: str) -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    if Console is None or Panel is None or Text is None:
        print(f"[{BOT_NAME}] [{timestamp}] {message}")
        return

    console = Console()
    title = Text(f"{BOT_NAME} {BOT_VERSION}", style="bold cyan")
    body = Text(message, style="bold white")
    body.append(f"\n\n[{timestamp}]", style="dim")
    panel = Panel(body, title=title, border_style="magenta")
    console.print(panel)


def send_notification(message: str) -> None:
    if sys.platform.startswith("linux") and shutil_which("notify-send"):
        try:
            subprocess.run(
                ["notify-send", BOT_NAME, message],
                check=False,
            )
        except OSError:
            print(f"[{BOT_NAME}] Notification failed.", file=sys.stderr)


def load_history(history: HistoryManager) -> None:
    history.load()


def save_history(history: HistoryManager, message: str) -> None:
    history.save(message)


def job(history: HistoryManager, log_path: str, promo_counter: List[int]) -> None:
    try:
        promo_counter[0] += 1
        message = generate_message(history, promo_counter[0])
        if any(message in promo for promo in PROMOS_EN + PROMOS_TR):
            promo_counter[0] = 0
        display_terminal_ui(message)
        send_notification(message)
        save_log(message, log_path)
        save_history(history, message)
    except Exception as exc:  # pragma: no cover - resilience
        print(f"[{BOT_NAME}] Error: {exc}", file=sys.stderr)


def scheduler_loop(history: HistoryManager, log_path: str) -> None:
    promo_counter = [0]
    if schedule is None:
        print(f"[{BOT_NAME}] schedule not installed, falling back to sleep loop.")
        while True:
            job(history, log_path, promo_counter)
            time.sleep(INTERVAL_MINUTES * 60)

    schedule.every(INTERVAL_MINUTES).minutes.do(job, history, log_path, promo_counter)

    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as exc:  # pragma: no cover - resilience
            print(f"[{BOT_NAME}] Scheduler error: {exc}", file=sys.stderr)
            time.sleep(5)


def shutil_which(binary: str) -> str | None:
    for path in os.environ.get("PATH", "").split(os.pathsep):
        candidate = os.path.join(path, binary)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="m0tive v2 motivational bot")
    parser.add_argument("--language", default=LANGUAGE, help="en, tr, or multi")
    parser.add_argument("--interval", type=int, default=INTERVAL_MINUTES, help="Interval in minutes")
    parser.add_argument("--log-file", default=LOG_FILE, help="Log file path")
    parser.add_argument("--history-file", default=HISTORY_FILE, help="History file path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    global LANGUAGE
    global INTERVAL_MINUTES

    LANGUAGE = args.language
    INTERVAL_MINUTES = args.interval

    history = HistoryManager(args.history_file, RECENT_HISTORY_LIMIT)
    load_history(history)
    scheduler_loop(history, args.log_file)


if __name__ == "__main__":
    main()
