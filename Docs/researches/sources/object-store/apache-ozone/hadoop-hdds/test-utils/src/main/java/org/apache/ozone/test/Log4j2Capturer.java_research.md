# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/Log4j2Capturer.java

Purpose: `Log4j2Capturer` is a singleton Log4j2 implementation of `GenericTestUtils.LogCapturer` that captures Log4j2 output into an in-memory writer.

Important APIs and types: It uses Log4j2 core `LoggerContext`, `Configuration`, `LoggerConfig`, `Appender`, `WriterAppender`, and `PatternLayout`. The appender name is fixed as `capture`.

Control flow: The private singleton constructor calls `addAppender`, which creates and starts a writer appender, adds it to the configuration, then attaches it to every configured logger and the root logger. `stopCapturing` removes the named appender from all logger configs and root.

State and persistence behavior: No durable state. Runtime state is singleton capture writer and logger configuration mutations across the JVM. Because the instance is static, captured output can survive across uses unless cleared.

Dependencies and integration points: `GenericTestUtils.LogCapturer.log4j2` returns this singleton. The method currently ignores the requested logger name, so capture is broad.

Risks: The TODO notes it does not capture only a specific logger. Singleton behavior can cross-contaminate tests if output is not cleared. It mutates all logger configs and does not call `context.updateLoggers` explicitly after changes.

Test signals: Captured Log4j2 output appears in `getOutput`, and `stopCapturing` removes the capture appender from logger configs.
