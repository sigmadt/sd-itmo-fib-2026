/*
 * Сценарий: заказ отправлен, уведомляем покупателя и склад.
 *
 * Запуск: ./check.sh (компилирует и сравнивает вывод с эталоном)
 */

import java.io.FileDescriptor;
import java.io.FileOutputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;

public class Main {

    public static void main(String[] args) {
        // Печатаем в UTF-8, чтобы русский текст не ломался в консоли Windows и в IDE
        System.setOut(new PrintStream(new FileOutputStream(FileDescriptor.out), true, StandardCharsets.UTF_8));

        AppConfig config = AppConfig.getInstance();
        config.logEnabled = true;
        config.maxRetries = 2;

        Notifier notifier = new Notifier();
        int orderId = 1042;

        // Покупателю: письмо и SMS
        Message email = new Message("anna@example.com", "Заказ " + orderId,
                "Заказ " + orderId + " отправлен. Трек-номер RB123456",
                "orders@example.com", "high", false, null, null, true, null);
        notifier.send("email", email);

        Message sms = new Message("+7 (900) 111-22-30", "", "Заказ " + orderId + " отправлен",
                null, "high", false, null, null, false, null);
        notifier.send("sms", sms);

        // Склад: в Telegram, у склада есть вложенная группа
        Map<String, Object> warehouse = Map.of(
                "name", "Склад",
                "members", List.of(
                        "@petrov",
                        Map.of("name", "Ночная смена", "members", List.of("@ivanova", "@sidorov"))));
        Notifier.notifyGroup(notifier, "telegram", warehouse, "Собрать заказ " + orderId);

        // Менеджеру: срочно, с шаблоном и подписью отдела
        Message manager = new Message("@manager", "", "Заказ " + orderId + " отправлен", null,
                "high", false, 0, "Срочно: {body}", false,
                "Отдел логистики");
        notifier.send("telegram", manager);

        System.out.println("Отправлено сообщений: " + config.sentCount);
    }
}
