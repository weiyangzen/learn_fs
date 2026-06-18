# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/audit/DummyAction.java

Purpose: Test enum implementing `AuditAction` for representative audit operations.

Important APIs/types/functions: Enum constants for create/read/update/delete volume, bucket, key operations plus owner/quota changes; `getAction`.

Control flow: `getAction` returns the enum constant string.

State and persistence behavior: Stateless enum values.

Dependencies and integration points: Used by audit message tests to avoid binding to production-specific actions while exercising `AuditAction`.

Risks: Dummy action names may drift from real audit operation vocabulary, but they intentionally provide generic coverage.

Test signals: Supplies deterministic action strings for audit logger formatting and exclusion tests.
