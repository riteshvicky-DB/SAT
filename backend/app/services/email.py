import asyncio
import logging

import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def send_reset_email(to_email: str, reset_url: str, name: str = "Student") -> bool:
    settings = get_settings()
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "SAT Academy — Reset your password"
    msg["From"] = settings.smtp_from
    msg["To"] = to_email

    text = f"""Hi {name},

You requested a password reset for your SAT Academy account.

Click the link below to set a new password (valid for 30 minutes):
{reset_url}

If you didn't request this, ignore this email.

— SAT Academy Team
"""
    html = f"""
<html><body style="font-family:sans-serif;max-width:520px;margin:auto;padding:24px">
  <h2 style="color:#6c5ce7">SAT Academy</h2>
  <p>Hi <strong>{name}</strong>,</p>
  <p>You requested a password reset. Click the button below — the link expires in <strong>30 minutes</strong>.</p>
  <a href="{reset_url}" style="display:inline-block;margin:16px 0;padding:12px 28px;background:#6c5ce7;color:#fff;border-radius:10px;text-decoration:none;font-weight:600">
    Reset Password
  </a>
  <p style="color:#aaa;font-size:12px">If you didn't request this, you can safely ignore this email.</p>
</body></html>
"""
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_pass,
            start_tls=True,
        )
        logger.info("Reset email sent to %s", to_email)
        return True
    except Exception as exc:
        logger.error("Failed to send reset email to %s: %s", to_email, exc)
        return False


async def send_welcome_email(to_email: str, name: str) -> bool:
    settings = get_settings()
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Welcome to SAT Academy!"
    msg["From"] = settings.smtp_from
    msg["To"] = to_email

    html = f"""
<html><body style="font-family:sans-serif;max-width:520px;margin:auto;padding:24px">
  <h2 style="color:#6c5ce7">Welcome to SAT Academy, {name}!</h2>
  <p>Your account is ready. Start practicing at <a href="http://localhost:5173">SAT Academy</a>.</p>
  <p style="color:#aaa;font-size:12px">This is a local offline app — all your data stays on your device.</p>
</body></html>
"""
    msg.attach(MIMEText(html, "html"))
    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_pass,
            start_tls=True,
        )
        return True
    except Exception as exc:
        logger.error("Welcome email failed: %s", exc)
        return False
