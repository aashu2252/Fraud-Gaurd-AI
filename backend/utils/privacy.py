import hashlib
import hmac
from config import get_settings

settings = get_settings()


def hash_identity(identifier: str, salt: str = None) -> str:
    """
    Privacy-preserving identity hashing using HMAC-SHA256.

    This is the core of the "Inventive Step" for the patent:
    - Store A and Store B can both hash the same email with the same shared salt.
    - The resulting hash is IDENTICAL → same user is recognized across stores.
    - But neither store (nor the AI system) ever sees the raw email/phone.
    - Without the salt, the hash cannot be reversed or linked to a real identity.

    Args:
        identifier: Raw PII (email or phone number)
        salt: Optional custom salt; falls back to SALT_SECRET from .env

    Returns:
        64-character hex string (SHA-256 output)
    """
    _salt = (salt or settings.salt_secret).encode("utf-8")
    _identifier = identifier.strip().lower().encode("utf-8")
    digest = hmac.new(_salt, _identifier, hashlib.sha256).hexdigest()
    return digest


def verify_hash(identifier: str, expected_hash: str, salt: str = None) -> bool:
    """Constant-time comparison to verify a hash without timing attacks."""
    computed = hash_identity(identifier, salt)
    return hmac.compare_digest(computed, expected_hash)
