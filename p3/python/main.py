"""Сценарий: заказ отправлен, уведомляем покупателя и склад.

Запуск: python3 main.py
"""

from notifier import AppConfig, Message, Notifier, notify_group


def main():
    config = AppConfig()
    config.log_enabled = True
    config.max_retries = 2

    notifier = Notifier()
    order_id = 1042

    # Покупателю: письмо и SMS
    email = Message("anna@example.com", f"Заказ {order_id}",
                    f"Заказ {order_id} отправлен. Трек-номер RB123456",
                    "orders@example.com", "high", False, None, None, True, None)
    notifier.send("email", email)

    sms = Message("+7 (900) 111-22-30", "", f"Заказ {order_id} отправлен",
                  None, "high", False, None, None, False, None)
    notifier.send("sms", sms)

    # Склад: в Telegram, у склада есть вложенная группа
    warehouse = {
        "name": "Склад",
        "members": [
            "@petrov",
            {"name": "Ночная смена", "members": ["@ivanova", "@sidorov"]},
        ],
    }
    notify_group(notifier, "telegram", warehouse, f"Собрать заказ {order_id}")

    # Менеджеру: срочно, с шаблоном и подписью отдела
    manager = Message("@manager", "", f"Заказ {order_id} отправлен", None,
                      "high", False, 0, "Срочно: {body}", False,
                      "Отдел логистики")
    notifier.send("telegram", manager)

    print(f"Отправлено сообщений: {config.sent_count}")


if __name__ == "__main__":
    main()
