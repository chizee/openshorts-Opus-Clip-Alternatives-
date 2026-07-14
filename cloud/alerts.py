"""Operational email alerts for the admin (proxy out of credits, high failure rate).

Tracks recent managed-job outcomes in memory and emails ADMIN_EMAIL (via Resend)
when something looks broken, with a per-alert cooldown so it never spams.
"""
import time
from collections import deque

from .config import settings
from .emails import send_email

_recent = deque(maxlen=12)          # rolling window of recent job outcomes (ok bool)
_last_alert = {}                    # alert kind -> last-sent epoch
_ALERT_COOLDOWN = 3600              # 1 hour between repeats of the same alert
_FAIL_WINDOW_MIN = 6               # need at least this many recent jobs to judge a rate
_FAIL_THRESHOLD = 5                # ...and this many failures among them

# Substrings that suggest the proxy itself failed (auth / balance / tunnel).
_PROXY_HINTS = ("proxy", "407", "proxyauthentication", "tunnel connection",
                "credit", "balance", "insufficient", "payment required")


def _looks_like_proxy_error(err: str) -> bool:
    e = (err or "").lower()
    return any(k in e for k in _PROXY_HINTS)


def _cooldown_ok(kind: str) -> bool:
    now = time.time()
    if now - _last_alert.get(kind, 0) < _ALERT_COOLDOWN:
        return False
    _last_alert[kind] = now
    return True


async def send_admin_alert(subject: str, body: str):
    to = settings.admin_email
    if not to or not settings.smtp_configured:
        print(f"⚠️  [ADMIN ALERT] {subject}\n{body[:500]}"
              + ("" if to else "  (set ADMIN_EMAIL + SMTP_* to email these)"))
        return
    html = f"<pre style='font:13px/1.5 monospace;white-space:pre-wrap'>{body}</pre>"
    await send_email(to, f"[OpenShorts] {subject}", html)


async def record_job_outcome(ok: bool, error_text: str = ""):
    """Record a managed job's result and fire an alert if the picture looks bad."""
    _recent.append(bool(ok))
    if ok:
        return

    # 1) Proxy / credits problem — most urgent, alert immediately.
    if _looks_like_proxy_error(error_text) and _cooldown_ok("proxy"):
        await send_admin_alert(
            "⚠️ Proxy error — DataImpulse may be out of credits",
            "A managed job failed with a proxy-related error. Check your residential "
            "proxy balance (DataImpulse) — downloads will keep failing until it's topped up.\n\n"
            f"Error:\n{error_text[:1200]}",
        )
        return

    # 2) High failure rate — the YouTube download path may be broken (arms race).
    recent = list(_recent)
    fails = recent.count(False)
    if len(recent) >= _FAIL_WINDOW_MIN and fails >= _FAIL_THRESHOLD and _cooldown_ok("failrate"):
        await send_admin_alert(
            "⚠️ High download failure rate",
            f"{fails} of the last {len(recent)} managed jobs failed. The YouTube "
            "download path may be broken (yt-dlp / PO-token change). A backend image "
            "rebuild usually pulls the yt-dlp fix.\n\n"
            f"Last error:\n{error_text[:1200]}",
        )
