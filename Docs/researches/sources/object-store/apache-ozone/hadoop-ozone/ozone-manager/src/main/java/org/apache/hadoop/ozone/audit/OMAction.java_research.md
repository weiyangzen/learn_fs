# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/audit/OMAction.java

## Purpose

`OMAction` enumerates audit action names for user/request-level Ozone Manager operations.

## Important APIs and Types

It implements `AuditAction` and exports many enum constants covering write actions, read actions, ACL operations, filesystem operations, S3 secrets, tenants, snapshots, upgrades, object tagging, and snapshot diff jobs. `getAction()` returns `this.toString()`.

## Control Flow

There is no branching beyond enum initialization. Audit code can call `getAction()` to obtain the serialized action name.

## State and Persistence

Enum constants are static process state. Their names become audit log values and may be consumed by downstream audit tooling.

## Dependencies and Integration Points

It depends on the Ozone audit `AuditAction` interface. OM request handlers and audit emitters use these constants to tag audit events.

## Risks and Edge Cases

Renaming constants changes audit log strings and can break external parsing. Missing constants for new OM operations cause inconsistent audit coverage.

## Test Signals

Tests should verify request handlers use the expected `OMAction` constants and that new user-visible operations add audit actions.
