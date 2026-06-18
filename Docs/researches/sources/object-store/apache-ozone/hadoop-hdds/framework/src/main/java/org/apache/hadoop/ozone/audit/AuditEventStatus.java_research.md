# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditEventStatus.java

## Purpose

`AuditEventStatus` defines standard audit result strings for success and failure. The complete 36-line source was read for this report.

## Important APIs, Types, and Functions

Enum constants are `SUCCESS("SUCCESS")` and `FAILURE("FAILURE")`; `getStatus()` returns the string.

## Control Flow

There is no dynamic control flow beyond enum construction.

## State and Persistence Behavior

The enum values are emitted into audit logs as the `ret` field.

## Dependencies and Integration Points

It is consumed by `AuditMessage.Builder.withResult` and component audit builders.

## Risks and Edge Cases

Changing strings would break audit log expectations and parsers.

## Test Signals

Tests should verify message formatting includes `ret=SUCCESS` or `ret=FAILURE` and that downstream log parsers expect these exact values.
