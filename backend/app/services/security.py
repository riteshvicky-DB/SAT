import base64
import hashlib
import hmac

from app.core.config import get_settings


def local_digest(value: str) -> str:
    key = get_settings().encryption_key.encode()
    digest = hmac.new(key, value.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode()
