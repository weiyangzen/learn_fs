# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/Auditor.java

## Purpose

`Auditor` is an interface for service actors that can build audit messages for successful and failed operations. The complete 33-line source was read for this report.

## Important APIs, Types, and Functions

It declares `buildAuditMessageForSuccess(AuditAction, Map<String,String>)` and `buildAuditMessageForFailure(AuditAction, Map<String,String>, Throwable)`.

## Control Flow

There is no implementation flow. Components implement these methods to centralize audit message construction.

## State and Persistence Behavior

The interface owns no state. Implementations provide metadata that is later persisted to audit logs.

## Dependencies and Integration Points

It depends on `AuditAction`, `AuditMessage`, and Java maps. It integrates with `AuditLogger` use in Ozone services.

## Risks and Edge Cases

Implementations must consistently include user, IP, parameters, and result status. Missing or inconsistent fields reduce audit value and parser reliability.

## Test Signals

Tests should cover component implementations for success/failure message fields, throwable propagation, and sensitive parameter filtering.
