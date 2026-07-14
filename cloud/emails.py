"""Transactional + operational email via SMTP (e.g. Namecheap Private Email).

If SMTP isn't configured (local dev), messages are printed to the server log so
the magic-link flow and alerts still work without a real mailbox.
"""
import asyncio
import smtplib
import ssl
from email.message import EmailMessage

from .config import settings


def _send_sync(to: str, subject: str, html: str):
    msg = EmailMessage()
    msg["From"] = settings.email_from
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content("This message requires an HTML-capable email client.")
    msg.add_alternative(html, subtype="html")

    if settings.smtp_port == 465:
        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port,
                              context=ssl.create_default_context(), timeout=20) as s:
            s.login(settings.smtp_user, settings.smtp_password)
            s.send_message(msg)
    else:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as s:
            s.starttls(context=ssl.create_default_context())
            s.login(settings.smtp_user, settings.smtp_password)
            s.send_message(msg)


async def send_email(to: str, subject: str, html: str):
    """Send an email (async wrapper). Logs instead of sending if SMTP is unset."""
    if not settings.smtp_configured:
        print(f"✉️  [DEV email → {to}] {subject}")
        return
    try:
        await asyncio.to_thread(_send_sync, to, subject, html)
    except Exception as e:
        print(f"⚠️  Failed to send email to {to}: {e}")


async def send_magic_link_email(email: str, link: str):
    if not settings.smtp_configured:
        print(f"✉️  [DEV magic link] {email} -> {link}")
        return
    html = f"""
      <div style="font-family:system-ui,sans-serif;max-width:480px;margin:0 auto">
        <h2>Sign in to OpenShorts</h2>
        <p>Click the button below to sign in. This link expires in 15 minutes.</p>
        <p><a href="{link}" style="display:inline-block;background:#111;color:#fff;
           padding:12px 20px;border-radius:8px;text-decoration:none">Sign in</a></p>
        <p style="color:#666;font-size:13px">If you didn't request this, ignore this email.</p>
      </div>
    """
    await send_email(email, "Your OpenShorts sign-in link", html)
