import base64

from Crypto.Cipher import DES

from .config import CryptoConfig

_ZPAD = lambda d, s: d + b'\x00' * (-len(d) % s)


def encrypt_field(key: str, data: bytes) -> str:
    raw = DES.new(key.encode(), DES.MODE_ECB).encrypt(_ZPAD(data, 8))
    return base64.b64encode(raw).decode()


def derive_key(register_detail: dict) -> str:
    k_b64 = register_detail['k']
    k_len = register_detail['l']
    decoded = base64.b64decode(k_b64)
    raw = DES.new(CryptoConfig.DES_ROOT_KEY.encode(), DES.MODE_ECB).decrypt(decoded)
    return raw[:k_len].decode()
