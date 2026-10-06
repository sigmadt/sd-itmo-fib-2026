"""Сервис уведомлений интернет-магазина.

Отправляет уведомления о заказах на почту, по SMS и в Telegram.
Сеть не используется: каналы печатают, что бы они отправили.
"""

from legacy_sms import LegacySmsGateway


class AppConfig:
    """Настройки приложения, один объект на всю программу."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.sender_email = "shop@example.com"
            cls._instance.max_retries = 2
            cls._instance.log_enabled = True
            cls._instance.sent_count = 0
        return cls._instance


class Message:
    def __init__(self, to, subject, body, cc=None, priority="normal",
                 silent=False, retries=None, template=None, signature=True,
                 footer=None):
        self.to = to
        self.subject = subject
        self.body = body
        self.cc = cc
        self.priority = priority
        self.silent = silent
        self.retries = retries
        self.template = template
        self.signature = signature
        self.footer = footer

    def text(self):
        text = self.body
        if self.template is not None:
            text = self.template.replace("{body}", self.body)
        if self.signature:
            text += "\nС уважением, магазин"
        if self.footer is not None:
            text += "\n" + self.footer
        return text


class Notifier:
    def send(self, channel_type, message):
        config = AppConfig()
        retries = config.max_retries if message.retries is None else message.retries

        if channel_type == "email":
            for attempt in range(retries + 1):
                if config.log_enabled:
                    print(f"[log] email, попытка {attempt + 1}, кому {message.to}")
                header = f"[email] from={config.sender_email} to={message.to}"
                if message.cc is not None:
                    header += f" cc={message.cc}"
                header += f' subject="{message.subject}" priority={message.priority}'
                print(header)
                for line in message.text().split("\n"):
                    print("  " + line)
                config.sent_count += 1
                return True
            return False

        elif channel_type == "sms":
            gateway = LegacySmsGateway()
            digits = "".join(ch for ch in message.to if ch.isdigit())
            payload = message.text().encode("cp1251")
            for attempt in range(retries + 1):
                if config.log_enabled:
                    print(f"[log] sms, попытка {attempt + 1}, кому {message.to}")
                status = gateway.transmit(digits, payload)
                if status == 200:
                    config.sent_count += 1
                    return True
            if config.log_enabled:
                print(f"[log] sms не доставлено: {message.to}")
            return False

        elif channel_type == "telegram":
            for attempt in range(retries + 1):
                if config.log_enabled:
                    print(f"[log] telegram, попытка {attempt + 1}, кому {message.to}")
                line = f"[telegram] {message.to}: {message.text()}"
                if message.silent:
                    line += " (без звука)"
                print(line)
                config.sent_count += 1
                return True
            return False

        else:
            raise ValueError(f"Неизвестный канал: {channel_type}")


def notify_group(notifier, channel_type, group, text):
    """Отправляет текст всем в группе. Группа может содержать другие группы."""
    if isinstance(group, str):
        message = Message(group, "", text, None, "normal", True, None, None, False, None)
        notifier.send(channel_type, message)
    elif isinstance(group, dict):
        print(f"[group] {group['name']}")
        for member in group["members"]:
            notify_group(notifier, channel_type, member, text)
    else:
        raise TypeError(f"Непонятный получатель: {group!r}")
