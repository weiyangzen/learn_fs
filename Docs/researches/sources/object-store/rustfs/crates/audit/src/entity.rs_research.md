# sources/object-store/rustfs/crates/audit/src/entity.rs

## Purpose

`entity.rs` defines the serializable audit event contract for RustFS. It models object versions, API details, and full audit entries, plus builders used by request handling code to construct audit logs without manually filling every optional field.

## Important APIs and Types

`ObjectVersion` serializes as `{objectName, versionId?}` and has a `new` constructor. `ApiDetails` carries API name, bucket/object/object-list, status/status code, byte counters, header bytes, and latency strings; `ApiDetailsBuilder` provides chainable setters and `build`.

`AuditEntry` is the top-level audit log payload. Required fields are `version`, millisecond timestamp, S3 `EventName`, `trigger`, and `api`; optional fields include deployment/site, type, remote host, historical `requestID`, user agent, request path/host/node, claims/query/headers, response headers, tags, access key, parent user, and error. `AuditEntryBuilder::new` sets required fields and `Utc::now`, while chainable setters fill optional fields or override required fields.

## Control Flow

There is no asynchronous control flow. Callers build `ApiDetails`, then pass it with version/event/trigger into `AuditEntryBuilder::new`, optionally chain metadata setters, and serialize the resulting `AuditEntry` through serde before dispatching it to audit targets.

## State and Persistence

The file owns only data structures. Persistence is external: serialized `AuditEntry` values may be sent to audit targets, replay queues, logs, or external systems. `skip_serializing_if` keeps absent optional fields out of the JSON contract, and `chrono::serde::ts_milliseconds` fixes timestamp serialization.

## Dependencies and Integration Points

It depends on `chrono` for UTC timestamps, `hashbrown::HashMap`, `rustfs_s3_types::EventName`, `serde`, and `serde_json::Value`. It integrates with the pipeline through `EntityTarget<AuditEntry>`, with target plugins that serialize audit payloads, and with tests that protect external field names.

## Risks and Edge Cases

The serde field names are part of an external audit contract. The `request_id` field intentionally serializes as `requestID`, and accidental renames would break consumers. Several duration fields are strings rather than numeric types, so producers must keep formatting consistent. `Default` can create structurally incomplete audit entries if used directly instead of builders. Header/claim/tag maps can contain sensitive values unless callers sanitize before building the entry.

## Test Signals

Existing unit coverage verifies `requestID` serialization and absence of `request_id`. Additional useful tests should verify timestamp millisecond encoding, optional-field omission, builder setter coverage, object version field names, and JSON compatibility with expected external audit schemas.
