public class Message {

    public String to;
    public String subject;
    public String body;
    public String cc;
    public String priority;
    public boolean silent;
    public Integer retries;
    public String template;
    public boolean signature;
    public String footer;

    public Message(String to, String subject, String body) {
        this(to, subject, body, null, "normal");
    }

    public Message(String to, String subject, String body, String cc, String priority) {
        this(to, subject, body, cc, priority, false, null, null, true, null);
    }

    public Message(String to, String subject, String body, String cc, String priority,
                   boolean silent, Integer retries, String template, boolean signature,
                   String footer) {
        this.to = to;
        this.subject = subject;
        this.body = body;
        this.cc = cc;
        this.priority = priority;
        this.silent = silent;
        this.retries = retries;
        this.template = template;
        this.signature = signature;
        this.footer = footer;
    }

    public String text() {
        String text = body;
        if (template != null) {
            text = template.replace("{body}", body);
        }
        if (signature) {
            text += "\nС уважением, магазин";
        }
        if (footer != null) {
            text += "\n" + footer;
        }
        return text;
    }
}
