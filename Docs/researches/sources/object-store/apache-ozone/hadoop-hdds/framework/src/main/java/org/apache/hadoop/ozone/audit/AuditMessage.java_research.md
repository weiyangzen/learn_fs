# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditMessage.java

## Purpose

`AuditMessage` is the log4j2 `Message` implementation for structured Ozone audit records. It formats user, IP, operation, JSON parameters, result, optional performance details, and optional throwable. The complete 149-line source was read for this report.

## Important APIs, Types, and Functions

Important APIs are `getFormattedMessage`, `getThrowable`, `getOp`, and nested `Builder` methods `setUser`, `atIp`, `forOperation`, `withParams`, `getParams`, `withResult`, `withException`, `setPerformance`, and `build`.

## Control Flow

The constructor memoizes message formatting via Ratis `MemoizedSupplier`, so repeated logging calls reuse the same formatted string. `formMessage` builds the audit format. Parameters are serialized with Jackson `ObjectMapper`; if JSON serialization fails, it falls back to `Map.toString()`.

## State and Persistence Behavior

State is immutable after construction except for lazy memoized message computation. Formatted output persists in audit logs through `AuditLogger`.

## Dependencies and Integration Points

It depends on Jackson, log4j2 `Message`, `AuditAction`, `AuditEventStatus`, `AuditLogger.PerformanceStringBuilder`, and Ratis memoization. Component `Auditor` implementations build it.

## Risks and Edge Cases

The builder does not validate required fields, so null user/IP/op/result can appear in logs. JSON serialization order depends on map implementation. Parameter values must avoid sensitive data unless callers filter them. Output format is parser-sensitive.

## Test Signals

Tests should verify full and minimal formatting, JSON fallback, throwable exposure, memoization, performance suffixes, and compatibility with documented audit parser expectations.
