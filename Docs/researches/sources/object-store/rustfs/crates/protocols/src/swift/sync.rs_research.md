# sources/object-store/rustfs/crates/protocols/src/swift/sync.rs

Defines configuration and helper logic for Swift container synchronization. The file models sync metadata, sync status, retry queue entries, conflict-resolution rules, target URL parsing, and HMAC signatures, but does not implement a background replication worker.

Important API surface: `SyncConfig::from_metadata`, `to_metadata`, and `validate` manage `x-container-sync-to` and `x-container-sync-key`. `SyncStatus` records last success, synced count, failures, last error, and queue size. `SyncQueueEntry` tracks object, etag, last modified, retry count, and next retry, with exponential backoff helpers. `ConflictResolution` and `resolve_conflict()` encode local/remote precedence. `extract_target_container()` parses target URLs. `generate_sync_signature()` and `verify_sync_signature()` use HMAC-SHA1 over the request path.

Control flow: metadata parsing returns `Ok(None)` when no sync target exists, errors when a target lacks a key, and constructs an enabled config otherwise. Retry scheduling increments the retry count and caps backoff at one hour. Conflict resolution returns whether the local object should win. Signature verification regenerates and compares hex signatures.

Persistent state is not implemented here. Sync configuration is represented as container metadata headers; queue and status persistence are left to a future worker. Dependencies are Swift errors, `HashMap`, tracing, `hmac`, `sha1`, and `hex`.

Risks: the module documentation describes bidirectional background sync and convergence, but the file only supplies primitives. HMAC comparison is ordinary string equality, not constant-time. URL validation checks only HTTP(S) prefix and path shape. Short sync keys only warn. Retry backoff assumes callers respect the max-retry policy.

Tests cover metadata parsing, validation, status counters, retry backoff/readiness/max retries, conflict strategies, target container extraction, signature generation, and verification.
