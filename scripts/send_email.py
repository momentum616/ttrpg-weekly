"""
Send an editor notification for a generated research draft.

The MVP supports Resend or SMTP. If no email provider is configured, the script
prints the email content and exits successfully so draft generation is not
blocked during early testing.
"""

from __future__ import annotations

import argparse
import json
import os
import smtplib
import ssl
import sys
import urllib.error
import urllib.request
from email.message import EmailMessage
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a draft-ready email.")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body-file", required=True)
    parser.add_argument("--to", default=os.getenv("EDITOR_EMAIL", ""))
    return parser.parse_args()


def send_resend(to_email: str, subject: str, body: str) -> bool:
    api_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv("EMAIL_FROM")
    if not api_key or not from_email:
        return False

    payload = {
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "text": body,
    }
    request = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            print(response.read().decode("utf-8"))
        return True
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Resend API request failed: {exc.code} {body_text}") from exc


def send_smtp(to_email: str, subject: str, body: str) -> bool:
    host = os.getenv("SMTP_HOST")
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("EMAIL_FROM")
    if not host or not username or not password or not from_email:
        return False

    port = int(os.getenv("SMTP_PORT", "587"))
    message = EmailMessage()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP(host, port, timeout=60) as server:
        server.starttls(context=context)
        server.login(username, password)
        server.send_message(message)
    return True


def main() -> int:
    args = parse_args()
    body = Path(args.body_file).read_text(encoding="utf-8")
    if not args.to:
        print("EDITOR_EMAIL is not set; skipping email notification.")
        print(body)
        return 0

    if send_resend(args.to, args.subject, body):
        print("Email sent with Resend.")
        return 0
    if send_smtp(args.to, args.subject, body):
        print("Email sent with SMTP.")
        return 0

    print("No email provider configured; skipping email notification.")
    print(body)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
