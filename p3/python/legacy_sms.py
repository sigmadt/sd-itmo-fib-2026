"""Библиотека SMS-провайдера.

Это чужой код. Менять его нельзя, можно только вызывать.
"""


class LegacySmsGateway:
    """Шлюз SMS от провайдера.

    transmit(msisdn, payload) -> int
      msisdn: номер телефона, только цифры, например "79001112230"
      payload: текст сообщения в кодировке cp1251
      возвращает код ответа: 200 доставлено, 503 провайдер временно недоступен
    """

    _calls = {}

    def transmit(self, msisdn, payload):
        calls = LegacySmsGateway._calls.get(msisdn, 0)
        LegacySmsGateway._calls[msisdn] = calls + 1
        # Провайдер иногда отвечает 503 с первого раза
        if msisdn.endswith("0") and calls == 0:
            print(f"[sms-gateway] 503 для {msisdn}")
            return 503
        print(f"[sms] {msisdn}: {payload.decode('cp1251')}")
        return 200
