/*
 * Сервис уведомлений интернет-магазина.
 *
 * Отправляет уведомления о заказах на почту, по SMS и в Telegram.
 * Сеть не используется: каналы печатают, что бы они отправили.
 */

import java.nio.charset.Charset;
import java.util.List;
import java.util.Map;

public class Notifier {

    public boolean send(String channelType, Message message) {
        AppConfig config = AppConfig.getInstance();
        int retries = message.retries == null ? config.maxRetries : message.retries;

        if (channelType.equals("email")) {
            for (int attempt = 0; attempt < retries + 1; attempt++) {
                if (config.logEnabled) {
                    System.out.println("[log] email, попытка " + (attempt + 1) + ", кому " + message.to);
                }
                String header = "[email] from=" + config.senderEmail + " to=" + message.to;
                if (message.cc != null) {
                    header += " cc=" + message.cc;
                }
                header += " subject=\"" + message.subject + "\" priority=" + message.priority;
                System.out.println(header);
                for (String line : message.text().split("\n", -1)) {
                    System.out.println("  " + line);
                }
                config.sentCount += 1;
                return true;
            }
            return false;

        } else if (channelType.equals("sms")) {
            LegacySmsGateway gateway = new LegacySmsGateway();
            StringBuilder digits = new StringBuilder();
            for (char ch : message.to.toCharArray()) {
                if (Character.isDigit(ch)) {
                    digits.append(ch);
                }
            }
            byte[] payload = message.text().getBytes(Charset.forName("windows-1251"));
            for (int attempt = 0; attempt < retries + 1; attempt++) {
                if (config.logEnabled) {
                    System.out.println("[log] sms, попытка " + (attempt + 1) + ", кому " + message.to);
                }
                int status = gateway.transmit(digits.toString(), payload);
                if (status == 200) {
                    config.sentCount += 1;
                    return true;
                }
            }
            if (config.logEnabled) {
                System.out.println("[log] sms не доставлено: " + message.to);
            }
            return false;

        } else if (channelType.equals("telegram")) {
            for (int attempt = 0; attempt < retries + 1; attempt++) {
                if (config.logEnabled) {
                    System.out.println("[log] telegram, попытка " + (attempt + 1) + ", кому " + message.to);
                }
                String line = "[telegram] " + message.to + ": " + message.text();
                if (message.silent) {
                    line += " (без звука)";
                }
                System.out.println(line);
                config.sentCount += 1;
                return true;
            }
            return false;

        } else {
            throw new IllegalArgumentException("Неизвестный канал: " + channelType);
        }
    }

    /** Отправляет текст всем в группе. Группа может содержать другие группы. */
    @SuppressWarnings("unchecked")
    public static void notifyGroup(Notifier notifier, String channelType, Object group, String text) {
        if (group instanceof String) {
            Message message = new Message((String) group, "", text, null, "normal", true, null, null, false, null);
            notifier.send(channelType, message);
        } else if (group instanceof Map) {
            Map<String, Object> dict = (Map<String, Object>) group;
            System.out.println("[group] " + dict.get("name"));
            for (Object member : (List<Object>) dict.get("members")) {
                notifyGroup(notifier, channelType, member, text);
            }
        } else {
            throw new IllegalArgumentException("Непонятный получатель: " + group);
        }
    }
}
