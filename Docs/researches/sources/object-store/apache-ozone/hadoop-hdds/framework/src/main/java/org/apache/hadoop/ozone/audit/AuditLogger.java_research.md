# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditLogger.java

## Purpose

`AuditLogger` wraps log4j2 `ExtendedLogger` for Ozone audit events, applying read/write/auth/performance markers, result-based log levels, and configurable debug-level operation filtering. The complete 242-line source was read for this report.

## Important APIs, Types, and Functions

Important methods are `logWriteSuccess`, `logWriteFailure`, `logAuthFailure`, `logReadSuccess`, `logReadFailure`, `logWrite`, `logPerformance`, `refreshDebugCmdSet`, and testing accessor `getLogger`. Nested `PerformanceStringBuilder` formats performance fields such as metadata latency, operation latency, pre-op latency, size, count, and stream mode.

## Control Flow

Construction selects the log4j2 logger by `AuditLoggerType` and loads debug command configuration. Success logs normally emit at INFO, but `shouldLogAtDebug` lowers configured operations to DEBUG. Failure and auth failure logs emit at ERROR with the throwable. `refreshDebugCmdSet` reads `ozone.audit.log.debug.cmd.list.<loggerType>` from a new or supplied `OzoneConfiguration` and atomically swaps a lowercase operation set.

## State and Persistence Behavior

The class owns an `ExtendedLogger`, logger type, atomic debug command set, and lowercase operation-name cache. Audit output is persisted according to log4j2 appenders configured outside this class. Performance string builders are per-message helpers.

## Dependencies and Integration Points

It depends on Ozone configuration, `AuditLoggerType`, `AuditMarker`, `AuditMessage`, log4j2 markers/levels, SLF4J, and Ratis/Java utilities. Component `Auditor` implementations build messages and call this logger.

## Risks and Edge Cases

Debug filtering lowercases operation strings and caches by original value; null operations would fail. `refreshDebugCmdSet()` without arguments creates a new configuration, which may not include dynamically supplied config in tests/services. Performance fields are formatted by string concatenation and not JSON. Audit parser compatibility makes output format changes high risk.

## Test Signals

Tests should verify marker/level selection, throwable propagation for failures, debug command refresh behavior, performance string formatting, operation-name case handling, and sample log format compatibility.
