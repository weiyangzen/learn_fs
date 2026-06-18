# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditLoggerType.java

## Purpose

`AuditLoggerType` enumerates named audit loggers for Ozone services. The complete 39-line source was read for this report.

## Important APIs, Types, and Functions

Constants are `DNLOGGER`, `OMLOGGER`, `SCMLOGGER`, `S3GLOGGER`, and `OMSYSTEMLOGGER`, each with a log4j2 logger name. `getType()` returns the configured name.

## Control Flow

Enum construction stores the logger name; `AuditLogger` uses it to fetch the corresponding log4j2 logger and debug config key suffix.

## State and Persistence Behavior

The enum has in-memory constant state only. Values select audit log destinations configured in log4j2.

## Dependencies and Integration Points

It integrates with `AuditLogger`, audit log4j2 properties, and Ozone service components.

## Risks and Edge Cases

Renaming values or type strings can break logging configuration and debug command configuration keys.

## Test Signals

Tests should verify each type maps to expected logger name and that `AuditLogger` resolves configured appenders/filters for those names.
