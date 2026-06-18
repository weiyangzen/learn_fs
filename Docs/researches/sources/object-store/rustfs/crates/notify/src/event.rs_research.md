# sources/object-store/rustfs/crates/notify/src/event.rs

## Purpose
Models S3-compatible notification events and builds them from RustFS object-operation context. It covers bucket/object metadata, request/response details, source information, event schema versioning, replication suppression hints, and restore-completed Glacier payloads.

## Important APIs, types, and functions
- Serializable structs: `Identity`, `Bucket`, `Object`, `Metadata`, `Source`, `GlacierEventData`, `RestoreEventData`, and `Event`.
- `Event::new_test_event` builds synthetic events for unit tests.
- `Event::mask` delegates to `EventName::mask`.
- `Event::new(EventArgs)` creates production events from `rustfs_ecstore::store_api::ObjectInfo`.
- `EventArgs` carries event name, bucket, object info, request params, response elements, version id, host, port, and user agent.
- `EventArgs::is_replication_request` only honors `x-rustfs-source-replication-request` values `true` or `1`.
- `EventArgsBuilder` provides fluent construction for callers and tests.

## Control flow
`Event::new` computes a sequencer from object mod time or current timestamp, ensures `x-amz-request-id` and `x-amz-id-2` response keys exist, URL-encodes the object key, extracts principal/region from request params, and fills bucket/object metadata. Removed-object events omit size, ETag, content type, and user metadata. Non-removed events copy object metadata except keys prefixed with `x-amz-meta-internal-`. Restore-completed events add `glacier_event_data` when both expiry and storage class/tier are available.

## State and persistence behavior
No durable state is managed. Event values are serialized outbound to notification targets and stored in target queues when targets have a backing store. The sequencer uses timestamp-derived values rather than a persisted monotonic counter.

## Dependencies and integration points
Depends on `chrono`, `time`, `url::form_urlencoded`, `hashbrown::HashMap`, `rustfs_s3_types::{EventName, event_schema_version}`, `rustfs_s3_ops::is_object_removed_event`, and `rustfs_ecstore::store_api::ObjectInfo`. It feeds `NotifyPipeline`, `EventNotifier`, target stores, and global `notifier_global::notify`.

## Risks and edge cases
The event object key is URL-encoded before dispatch; the rule engine must compensate by matching decoded keys when bucket filters are written against raw keys. Removed events intentionally omit object details, which affects consumers expecting size or ETag on deletes. Replication suppression only accepts the RustFS header, not MinIO compatibility headers, to avoid dropping normal console deletes. `timestamp_nanos_opt().unwrap_or(0)` can collapse sequencers to zero if chrono cannot represent the timestamp.

## Test signals
Tests assert AWS-compatible event schema versions, Glacier restore payload contents and formatting, and replication-header behavior including case-insensitive `true`, numeric `1`, falsey values, and ignored MinIO replication headers.
