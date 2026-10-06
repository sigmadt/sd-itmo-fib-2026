import java.nio.charset.Charset;
import java.util.HashMap;
import java.util.Map;

/**
 * Библиотека SMS-провайдера.
 *
 * Это чужой код. Менять его нельзя, можно только вызывать.
 *
 * transmit(msisdn, payload) возвращает int
 *   msisdn: номер телефона, только цифры, например "79001112230"
 *   payload: текст сообщения в кодировке windows-1251
 *   возвращает код ответа: 200 доставлено, 503 провайдер временно недоступен
 */
public class LegacySmsGateway {

    private static final Map<String, Integer> calls = new HashMap<>();

    public int transmit(String msisdn, byte[] payload) {
        int count = calls.getOrDefault(msisdn, 0);
        calls.put(msisdn, count + 1);
        // Провайдер иногда отвечает 503 с первого раза
        if (msisdn.endsWith("0") && count == 0) {
            System.out.println("[sms-gateway] 503 для " + msisdn);
            return 503;
        }
        System.out.println("[sms] " + msisdn + ": " + new String(payload, Charset.forName("windows-1251")));
        return 200;
    }
}
