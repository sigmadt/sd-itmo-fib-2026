# Шпаргалка по Mermaid

Диаграмма пишется в блоке кода с языком `mermaid`. Предпросмотр в VS Code: расширение `bierner.markdown-mermaid`, затем `Cmd/Ctrl+Shift+V`.

## Диаграмма классов

```mermaid
classDiagram
    class Channel {
        <<interface>>
        +send(message) bool
    }
    class EmailChannel {
        -config
        +send(message) bool
    }
    class Notifier {
        +send(channel_type, message)
    }

    Channel <|.. EmailChannel : реализует
    Notifier --> Channel : использует
```

| Связь | Как пишется | Что значит |
|---|---|---|
| Наследование | `Base <\|-- Child` | Child это Base |
| Реализация интерфейса | `Interface <\|.. Impl` | Impl выполняет контракт Interface |
| Композиция | `Owner *-- Part` | Part живет внутри Owner и без него не существует |
| Агрегация | `Group o-- Member` | Group содержит Member, но Member живет и сам |
| Ассоциация | `A --> B` | A хранит ссылку на B |
| Зависимость | `A ..> B` | A пользуется B (параметр, создание) |

Видимость: `+` публичное, `-` приватное. Подпись связи после двоеточия: `A --> B : создает`.

## Диаграмма последовательности

```mermaid
sequenceDiagram
    participant M as main
    participant N as Notifier
    participant G as LegacySmsGateway

    M->>N: send("sms", message)
    loop пока не доставлено, не больше retries+1 раз
        N->>G: transmit(digits, payload)
        alt доставлено
            G-->>N: 200
        else провайдер недоступен
            G-->>N: 503
        end
    end
    N-->>M: True
```

`->>` вызов, `-->>` ответ, `loop` повтор, `alt` / `else` развилка.

## Компонентная диаграмма

В Mermaid нет отдельного типа, используем `flowchart`:

```mermaid
flowchart LR
    main --> Notifier
    Notifier --> AppConfig
    Notifier --> LegacySmsGateway
    subgraph vendor [Чужой код]
        LegacySmsGateway
    end
```

Стрелка значит «использует». `LR` слева направо, `TD` сверху вниз.
