# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/TimedOutTestsListener.java

Purpose: `TimedOutTestsListener` is a JUnit Platform listener that prints full thread diagnostics to `System.err` when a test fails with `TimeoutException`.

Important APIs and types: It implements `TestExecutionListener`, handles `TestExecutionResult` and `TestIdentifier`, and uses `Thread.getAllStackTraces`, `ManagementFactory.getThreadMXBean`, `ThreadInfo`, `MonitorInfo`, and `LockInfo`. Static API `buildThreadDiagnosticString` is also used by wait utilities.

Control flow: `executionFinished` checks for failed results whose throwable is a `TimeoutException`, prints a banner, then prints diagnostics. Diagnostics include a timestamp, a thread dump built from all JVM stack traces, and optional monitor-deadlock details from `findMonitorDeadlockedThreads`.

State and persistence behavior: No durable state. It reads live JVM thread state and writes diagnostics to stderr. Date formatting uses a local `SimpleDateFormat` instance per call.

Dependencies and integration points: Integrated with JUnit Platform launcher configuration and `GenericTestUtils.waitFor`, which embeds thread diagnostics in timeout exceptions.

Risks: Thread dump output can be large. It detects monitor deadlocks but not all ownable-synchronizer deadlocks unless exposed through the selected MXBean call. Printing to global stderr can interleave under parallel test execution.

Test signals: On timeout failures, stderr contains the timeout banner, timestamp, thread stack traces, and deadlock section when applicable.
