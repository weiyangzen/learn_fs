# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/RequestAuditor.java

## Purpose

`RequestAuditor` is the audit-map contract implemented by OM request classes. It defines how request handlers build `OMAuditLogger` messages and provides default helpers for common volume and key audit fields.

## Important APIs, Types, And Functions

- `buildAuditMessage(AuditAction, Map<String,String>, Throwable, UserInfo)` is the main implementor hook for audit logging.
- `buildVolumeAuditMap(String)` is an implementor hook for volume-scoped operations.
- `buildLightKeyArgsAuditMap(KeyArgs)` emits volume, bucket, and key only.
- `buildKeyArgsAuditMap(KeyArgs)` extends the light map with data size, replication type/factor/config, rewrite generation, and the `ETAG` metadata item when present.

## Control Flow And State

The default helpers are null-safe and return empty maps for null `KeyArgs`. They use `LinkedHashMap` for populated key audit maps so audit output remains ordered. The implementation intentionally excludes most metadata and only promotes `ETAG`, keeping audit records useful without dumping arbitrary user metadata.

## Dependencies And Integration Points

The interface depends on Ozone protocol `KeyArgs` and `UserInfo`, audit abstractions, `OzoneConsts`, `HddsProtos`, and `ECReplicationConfig`. Request classes call these helpers when logging after lock release, usually with operation-specific `OMAction` values and captured exceptions.

## Risks And Test Signals

Risk centers on missing audit context after protocol changes. Tests should verify EC replication config is serialized, factor `ZERO` is omitted, rewrite generation and etag are included, null inputs are safe, and audit maps remain stable enough for log parsing.
