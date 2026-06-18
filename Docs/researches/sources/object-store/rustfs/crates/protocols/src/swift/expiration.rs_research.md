# sources/object-store/rustfs/crates/protocols/src/swift/expiration.rs

## Purpose
`expiration.rs` implements parsing and validation for Swift object expiration request headers. It converts `X-Delete-After` relative durations and `X-Delete-At` absolute Unix timestamps into metadata-ready expiration timestamps.

## Important APIs, Types, And Functions
`parse_delete_at` parses an unsigned Unix timestamp. `parse_delete_after` parses seconds from now and adds current Unix time. `extract_expiration` checks lowercase `x-delete-after` first, then `x-delete-at`, returning `Option<u64>`. `is_expired` compares a timestamp to current time. `validate_expiration` permits future timestamps and a 60-second clock skew, while logging far-future values more than ten years away.

## Control Flow
`object::put_object` calls `extract_expiration`, then `validate_expiration`, then stores `x-delete-at` in user metadata. Handler GET/HEAD helper paths surface stored `x-delete-at` as a direct `X-Delete-At` response header. `X-Delete-After` intentionally takes precedence over `X-Delete-At`.

## State, Persistence, And Dependencies
This module itself is stateless. Expiration state is persisted by `object.rs` as object user metadata. It depends only on system time, tracing, and Swift error/result types.

## Integration Points
The metadata written here is the intended input for `expiration_worker.rs`, although current worker storage integration is not wired to actual object scanning/deletion. Handler helper paths preserve the direct Swift header shape for `x-delete-at`; some older inline handler GET/HEAD code emits generic `x-object-meta-*` headers, creating a potential response inconsistency.

## Risks And Test Signals
Invalid non-UTF-8 header values are silently ignored by `extract_expiration` because it only parses when `to_str` succeeds. `parse_delete_after` uses unchecked `now + seconds`, so very large values can overflow in debug builds or wrap in release. The module validates syntax and timing but does not schedule deletion itself. Tests cover valid/invalid parsing, precedence, expiration comparison, clock-skew validation, far-future allowance, and no-header behavior.
