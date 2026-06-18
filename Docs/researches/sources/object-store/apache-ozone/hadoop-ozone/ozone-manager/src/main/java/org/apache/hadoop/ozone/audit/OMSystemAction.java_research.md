# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/audit/OMSystemAction.java

## Purpose

`OMSystemAction` enumerates audit action names for system-originated Ozone Manager events that are not direct user requests.

## Important APIs and Types

It implements `AuditAction` and defines constants such as `STARTUP`, `LEADER_CHANGE`, deletion cleanup actions, checkpoint installation, snapshot purge/move/set-property events, and key/directory deletion. `getAction()` returns `this.toString()`.

## Control Flow

No runtime branching exists beyond enum use by audit emitters.

## State and Persistence

Enum constants are static. Their string values are persisted in audit logs.

## Dependencies and Integration Points

It integrates with the same `AuditAction` abstraction as request-level `OMAction`, but is intended for system audit flows such as background services and leadership events.

## Risks and Edge Cases

Renames are audit compatibility changes. Missing actions can hide system operations from audit trails.

## Test Signals

Tests or audit assertions should verify background services and OM lifecycle flows emit these actions where required.
