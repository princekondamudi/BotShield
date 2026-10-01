import time
from db import conn

def score(signals: dict, ip: str, site_key: str):
    s = 0
    reasons = []

    if signals.get("honeypot"):
        s += 80; reasons.append("honeypot filled")
    if signals.get("fillTimeMs", 99999) < 2000:
        s += 40; reasons.append("filled too fast")
    if not signals.get("mouseMoves") and not signals.get("keyPresses"):
        s += 30; reasons.append("no human input events")
    if signals.get("webdriver"):
        s += 50; reasons.append("automation flag")

    ten_min_ago = int(time.time() * 1000) - 10 * 60 * 1000
    recent = conn.execute(
        "SELECT COUNT(*) c FROM events WHERE ip=? AND site_key=? AND created_at>?",
        (ip, site_key, ten_min_ago),
    ).fetchone()["c"]
    if recent >= 5:
        s += 40; reasons.append("too many submissions from IP")

    s = min(s, 100)
    verdict = "pass" if s < 30 else "challenge" if s < 70 else "block"
    return s, verdict, reasons




