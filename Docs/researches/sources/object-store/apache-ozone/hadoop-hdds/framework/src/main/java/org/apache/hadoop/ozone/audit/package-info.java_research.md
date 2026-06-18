# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/package-info.java

## Purpose

This package descriptor documents the Ozone audit logging framework, its log4j2 design, parser-sensitive format, marker filtering, and extension rules. The complete 142-line source was read for this report.

## Important APIs, Types, and Functions

It describes `Auditable`, `AuditAction`, `AuditEventStatus`, `AuditLogger`, `AuditLoggerType`, `AuditMarker`, `AuditMessage`, and `Auditor`, plus usage and extension guidance.

## Control Flow

There is no executable flow. The documented flow is: choose an `AuditLogger`, build an `AuditMessage`, log read/write success/failure, and rely on INFO/ERROR defaults plus marker filters.

## State and Persistence Behavior

The descriptor owns no state. It emphasizes that audit log output format is intended for future parser support and is persisted by log4j2 appenders.

## Dependencies and Integration Points

It documents integration with log4j2 properties, marker filters, asynchronous logging, and component action enums in OM/SCM/DN/S3G.

## Risks and Edge Cases

The file explicitly warns that changes can break logging. Key/value formatting constraints for auditable maps are parser-facing and should be treated as compatibility requirements.

## Test Signals

Tests should validate sample log4j2 configurations, marker filters, parser-compatible output, and extension instructions when new logger or marker types are added.
