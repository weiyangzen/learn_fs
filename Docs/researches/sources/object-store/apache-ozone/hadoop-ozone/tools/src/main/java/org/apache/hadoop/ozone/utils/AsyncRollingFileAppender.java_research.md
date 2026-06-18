# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/utils/AsyncRollingFileAppender.java

## Purpose
Log4j appender that lazily wraps a `RollingFileAppender` inside an `AsyncAppender`.

## Important APIs, types, and functions
Extends `AsyncAppender`, overrides `append`, and exposes synchronized getters/setters for max file size, backup index, file name, conversion pattern, blocking, and buffer size.

## Control flow
On first append, if no rolling appender exists, `createRollingFileAppender` synchronizes, builds a `PatternLayout`, creates a file appender in append mode, sets rolling limits, adds it to the async appender, then applies deferred blocking and buffer-size settings.

## State and persistence behavior
Persists log events to the configured file and rotates by max size/index. Configuration values are stored until first append.

## Dependencies and integration points
Uses reload4j/log4j `AsyncAppender`, `RollingFileAppender`, `PatternLayout`, and `LoggingEvent`.

## Risks and edge cases
Missing `fileName` causes runtime appender creation failure. Settings changed after the rolling appender is assigned may not propagate to the underlying appender. IOException is converted to unchecked `RuntimeException`.

## Test signals
No direct test in this subset. Signals would be log file creation, async buffering behavior, and rolling under configured size limits.
