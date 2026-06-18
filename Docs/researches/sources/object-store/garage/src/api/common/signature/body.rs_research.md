## sources/object-store/garage/src/api/common/signature/body.rs

Purpose: wraps request bodies after signature parsing so handlers can consume JSON, collected bytes, or streams while checksums are computed and verified.

Important APIs/types/functions: `ReqBody`, `StreamingChecksumReceiver`, `add_expected_checksums`, `add_md5`, `json`, `collect`, `collect_with_checksums`, and `streaming_with_checksums`.

Control flow: non-streaming `collect_with_checksums` consumes the boxed frame stream, updates checksummer with collected bytes, finalizes, and verifies expected checksums. Streaming mode creates an mpsc side channel: data/trailer frames are forwarded to a checksum task while the returned stream yields only data bytes to the caller. Trailer checksum values are extracted when a trailer frame appears.

State/persistence: per-request in-memory checksum state and expected checksum metadata. No durable state.

Dependencies/integration: created by `signature::streaming::parse_streaming_body`, consumed by S3/K2V handlers. Uses checksum helpers and common error traits.

Risks: `Mutex::into_inner().unwrap()` assumes uncontended ownership during consumption. Streaming checksum verification completes asynchronously through a join handle that callers must await when they need final checksums. Trailer algorithm unwrap assumes trailer frames only when configured.

Test signals: no local tests in this file; streaming parser tests exercise some body error paths indirectly.
