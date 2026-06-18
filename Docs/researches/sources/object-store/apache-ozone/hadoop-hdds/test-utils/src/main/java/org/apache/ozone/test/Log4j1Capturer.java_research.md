# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/Log4j1Capturer.java

Purpose: `Log4j1Capturer` is the Log4j1/reload4j implementation of `GenericTestUtils.LogCapturer`. It captures log output from a specific logger into an in-memory writer for assertions.

Important APIs and types: It uses Log4j1 `Logger`, `Appender`, `Layout`, `PatternLayout`, and `WriterAppender`. Constructors accept a logger and optional layout.

Control flow: Construction selects the root `stdout` or `console` appender layout when no layout is supplied, falls back to a default `PatternLayout`, creates a `WriterAppender` targeting the inherited `StringWriter`, and adds it to the target logger. `stopCapturing` removes that appender.

State and persistence behavior: No durable state. Runtime state is the installed appender and captured writer buffer. It mutates logger configuration until `stopCapturing` is called.

Dependencies and integration points: It is returned by `GenericTestUtils.LogCapturer.captureLogs` for Log4j1 and SLF4J-to-Log4j bridged loggers.

Risks: Forgetting to call `stopCapturing` leaves an appender attached and may duplicate log output or leak memory. It captures only the specified logger, and logger additivity/layout configuration affects content.

Test signals: Downstream tests inspect `getOutput`, call `clearOutput`, and stop capture after assertions.
