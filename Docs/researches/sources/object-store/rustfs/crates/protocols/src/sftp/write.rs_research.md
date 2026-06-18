# sources/object-store/rustfs/crates/protocols/src/sftp/write.rs

## Purpose
This file implements the write side of the RustFS SFTP gateway. It turns SFTP `OPEN`, `WRITE`, `CLOSE`, and large-copy behavior into S3-compatible `PutObject`, multipart upload, multipart completion, multipart abort, and multipart copy calls through the gateway `StorageBackend`. The core design is a sequential write state machine: small objects stay buffered until close and are committed with one `PutObject`; objects whose write buffer reaches `part_size` transition to multipart streaming and upload full parts as they arrive.

The module is also the cancellation-safety boundary for in-flight multipart uploads. Because request handlers temporarily remove write handles from the handle table while awaiting backend calls, this file builds "tombstone" `HandleState::Write` entries that carry the upload id and cached abort authorization. `driver.rs` consumes those tombstones from `Drop` to avoid orphaning multipart uploads when a session task is cancelled or disconnected mid-write.

## Important APIs, Types, And Functions
- `write_dispatch_byte_count`, `write_dispatch_append_bytes`, `write_dispatch_has_full_part`, and `fstat_reported_size` are small state-machine helpers over `WritePhase`. They implement offset accounting, append behavior, drain-loop decisions, and reported SFTP file size.
- `build_write_tombstone` constructs a failed write handle containing `upload_id` and `abort_authorized` for `Drop`.
- `rejects_excl_or_trunc_without_create` validates SFTP open-flag combinations.
- `should_abort_on_drop` returns an upload id only for `Streaming` or `Failed` phases whose cached abort probe allowed `AbortMultipartUpload`.
- `SftpDriver::open_write` validates paths, read-only mode, S3 `PutObject` authorization, and SFTP create/truncate semantics, then allocates a `HandleState::Write`.
- `SftpDriver::commit_write` performs the single-shot close-time `PutObject` path with metadata derived from SFTP attributes and retry on retryable S3 errors.
- `SftpDriver::start_multipart_upload`, `upload_multipart_bytes`, `finish_multipart_upload`, `abort_upload_with_auth`, and `close_abort_or_skip` wrap S3 multipart lifecycle operations with gateway authorization and error mapping.
- `SftpDriver::write_dispatch`, `write_dispatch_begin_streaming`, and `write_dispatch_flush_one_part` implement sequential writes, buffering-to-streaming transition, full-part upload, and failure poisoning.
- `SftpDriver::close_streaming` flushes a final partial part, completes multipart upload, or aborts/skips abort on failure according to the cached policy decision.
- `SftpDriver::multipart_copy` performs server-side copy for objects too large for single S3 copy by using multipart upload plus `UploadPartCopy` ranges.

## Control Flow
`open_write` first calls `enforce_server_readonly`, parses the SFTP path into bucket/key, rejects bucket-only opens, and authorizes `S3Action::PutObject`. It only accepts create-and-truncate semantics because the implementation replaces the whole object at close. `EXCLUDE` adds a best-effort `head_object` check: an existing object fails the open, a not-found result allows creation, and other S3 errors propagate. The handle starts in `WritePhase::Buffering` with empty `part_buffer`; selected open attributes are copied into the reported SFTP attributes and later converted to user metadata.

`write_dispatch` receives a write handle already removed from the table by the caller. It checks that the client offset exactly equals the current byte count, appends the incoming bytes, and loops while the buffer has at least `part_size` bytes. The first full part transitions from `Buffering` to `Streaming` by calling `start_multipart_upload`; after the upload id exists, a tombstone is inserted into the handle table before any later awaited part upload can be cancelled. Each full part is drained from the buffer and uploaded with `upload_multipart_bytes`, then its ETag is recorded as a `CompletedPart`. If upload fails, the phase becomes `Failed` with the upload id so close/drop can abort.

`commit_write` is the close path for handles that never entered multipart streaming. It wraps the buffered bytes in `Bytes` and rebuilds a single-use `StreamingBlob` per attempt. Retry is bounded by `COMMIT_WRITE_MAX_RETRIES` and `COMMIT_WRITE_BACKOFF_MS`, and is limited to errors recognized as retryable by `rustfs_utils::retry::is_s3code_in_message_retryable`. Non-retryable failures are immediately mapped through `s3_error_to_sftp`.

`close_streaming` handles multipart close by optionally uploading a final non-empty trailing buffer, enforcing the S3 multipart part cap for that final part, and then calling `finish_multipart_upload`. Any failure in final part upload or completion routes through `close_abort_or_skip`; that helper either re-authorizes and calls `AbortMultipartUpload` or logs a policy-respecting skip if the initial abort probe was denied.

`multipart_copy` computes an effective range size large enough to keep the copy within `S3_MAX_MULTIPART_PARTS` and not exceed `S3_MAX_PART_SIZE`. It creates a destination multipart upload, iterates byte ranges with `UploadPartCopy`, collects ETags, then completes or aborts the destination upload. Source data remains server-side.

## State And Persistence Behavior
The persistent state mutated by this file is object data and multipart upload state in the backing S3-compatible store. Buffered writes become one completed object through `PutObject`. Streaming writes create a multipart upload, stage uploaded parts, and either complete into the destination object or abort the upload. Failed or cancelled multipart uploads can leave staged parts only when abort is unauthorized or abort itself fails; the code explicitly expects bucket lifecycle cleanup for that policy pattern.

In-memory state lives in `HandleState::Write` and `WritePhase`: `Buffering` owns bytes not yet sent to S3; `Streaming` owns `upload_id`, `abort_authorized`, `part_buffer`, uploaded part metadata, and `next_part_number`; `Failed` preserves `upload_id` and abort policy after a part failure or as a cancellation tombstone. `attrs.size` is updated after successful writes using saturating byte-count logic; `fstat_reported_size` returns cached size for failed handles so clients see the last known successful byte count.

Open-time SFTP attributes are persisted as S3 user metadata by `sftp_attrs_to_user_metadata` on both single `PutObject` and `CreateMultipartUpload`. Multipart copy intentionally starts with empty SFTP attributes.

## Dependencies And Integration Points
The module depends on SFTP-specific path parsing, attribute conversion, state definitions, and error mapping from sibling modules. It integrates with `SftpDriver` handle allocation and handle-table management, `StorageBackend` S3 operations, gateway `S3Action` authorization, russh-sftp protocol types, `s3s::dto` builders, byte streams from `bytes`/`futures_util`, retry classification from `rustfs_utils`, and structured tracing.

It is tightly coupled to `driver.rs` because cancellation safety relies on the driver's drop-time scan using `should_abort_on_drop`. It also relies on caller discipline: removed handles must be reinserted or tombstoned around awaits according to the documented pattern.

## Risks And Edge Cases
- The write path only supports sequential overwrite semantics. Non-sequential offsets, append-like writes, or create-without-truncate are rejected to avoid silent data corruption.
- `EXCLUDE` is not atomic against a racing close-time `PutObject`; the code documents this as an S3 limitation.
- The multipart tombstone design is robust but subtle. Any future await inserted between upload id creation and tombstone insertion, or any remove-await-reinsert site that forgets the tombstone, can reintroduce orphaned uploads.
- `write_dispatch_flush_one_part` drains bytes before `UploadPart`; on failure the bytes are intentionally lost and the handle is poisoned. This is correct for abort semantics but means recovery must happen by restarting the upload, not continuing the handle.
- Abort authorization is cached by probing IAM before upload creation completes. Conditional IAM policies are not represented because gateway authorization passes empty conditions, so only unconditional allow/deny is honored.
- If abort is denied, failed or cancelled multipart uploads rely on lifecycle cleanup. Operators using deny-abort policies must configure cleanup rules.
- `commit_write` retries retryable backend messages but not run-backend deadline failures; a stalled backend becomes an immediate SFTP failure.
- Multipart copy guards oversized effective part sizes, but the comments note that an out-of-spec backend content length can still surface as generic failure.

## Test Signals
The file has extensive unit coverage under `#[cfg(test)]`. Tests cover helper arithmetic and failure behavior, transition tombstones before awaits, abort authorization caching, metadata preservation for single and multipart uploads, missing ETags, parts-limit failures with allowed and denied abort, complete/final-part failure abort paths, open-flag validation including `EXCLUDE`, cancellation mid-upload drop abort, retry behavior for `commit_write`, timeout handling, and non-retryable access-denied behavior. These tests strongly exercise state-machine edges, policy-sensitive abort behavior, and recent cancellation-safety invariants.
