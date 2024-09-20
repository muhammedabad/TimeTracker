from cryptography.fernet import Fernet
from django.conf import settings
from django.utils import timezone


class FernetCipher:
    def __init__(self):
        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())

    def encrypt_value(self, value: str) -> str:
        return self.cipher.encrypt(value.encode()).decode()

    def decrypt_value(self, value: str) -> str:
        return self.cipher.decrypt(value.encode()).decode()


def format_date(date_str: str) -> str:
    return timezone.datetime.strptime(date_str, "%Y-%m-%d").strftime("%d %b %Y")