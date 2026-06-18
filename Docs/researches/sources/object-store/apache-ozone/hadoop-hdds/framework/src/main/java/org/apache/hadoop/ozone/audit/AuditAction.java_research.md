# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditAction.java

## Purpose

`AuditAction` is the marker interface for component-specific audit operation enums. The complete 30-line source was read for this report.

## Important APIs, Types, and Functions

It declares one method: `String getAction()`.

## Control Flow

There is no control flow; enums in OM, SCM, datanode, and S3 gateway implement it to provide audit operation names.

## State and Persistence Behavior

It owns no state. Returned action names become part of audit log records.

## Dependencies and Integration Points

It is consumed by `AuditMessage.Builder.forOperation` and by component audit enums.

## Risks and Edge Cases

Action string stability matters because audit log parsing and debug-command filtering depend on operation names.

## Test Signals

Tests should ensure component action enums return expected stable strings and integrate with `AuditMessage` formatting/debug filters.
