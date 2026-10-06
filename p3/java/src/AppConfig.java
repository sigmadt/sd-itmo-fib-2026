/** Настройки приложения, один объект на всю программу. */
public class AppConfig {

    private static AppConfig instance;

    public String senderEmail = "shop@example.com";
    public int maxRetries = 2;
    public boolean logEnabled = true;
    public int sentCount = 0;

    private AppConfig() {
    }

    public static AppConfig getInstance() {
        if (instance == null) {
            instance = new AppConfig();
        }
        return instance;
    }
}
