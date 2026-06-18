# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/GenericTestUtils.java

Purpose: `GenericTestUtils` is a broad static utility class for Ozone tests. It provides timing helpers, wait loops, log-level manipulation, reflection helpers, log capture, standard stream capture, synthetic stdin, tee print streams, deterministic port allocation, and thread diagnostics through timeout failures.

Important APIs and types: Key APIs include `getTestStartTime`, `waitFor`, `assertThrows`, `setLogLevel`, `withLogDisabled`, `mockFieldReflection`, `getFieldReflection`, `getReverseMap`, nested `LogCapturer`, `PrintStreamCapturer`, `SystemErrCapturer`, `SystemOutCapturer`, `TeePrintStream`, `PortAllocator`, and `ReflectionUtils`. It bridges SLF4J to reload4j/Log4j1 and exposes a Log4j2 capture singleton.

Control flow: `waitFor` polls a boolean condition until true or timeout and includes a thread dump from `TimedOutTestsListener` on timeout. Reflection helpers temporarily make fields accessible and clear final modifiers, optionally spy the field value with Mockito, then restore metadata. Stream capturers replace global system streams with tee streams and restore them on close. `supplyOnSystemIn` replaces `System.in` with a newline-joined stream.

State and persistence behavior: There is no durable state, but the class mutates JVM-global state: logger levels and appenders, `System.in/out/err`, and static port allocation. `PortAllocator.NEXT_PORT` monotonically advances and wraps in a fixed range.

Dependencies and integration points: It integrates Guava preconditions, Apache Commons IO, Mockito, JUnit, Ratis checked suppliers, Log4j1, SLF4J, and the local timeout listener. Many tests use it for asynchronous waits and output/log assertions.

Risks: Global stream and logger changes require disciplined close/finally handling. Reflection utilities depend on JDK internals, including Java 9 fallback access to `Class.getDeclaredFields0`. `PortAllocator` does not reserve sockets, so allocated ports can still race with other processes.

Test signals: Downstream tests signal correctness by reliable waits, restored globals, captured output/log content, successful final-field spying, and useful timeout diagnostics.
