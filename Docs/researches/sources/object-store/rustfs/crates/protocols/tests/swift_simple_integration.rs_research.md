# sources/object-store/rustfs/crates/protocols/tests/swift_simple_integration.rs

## Purpose

This Swift-feature-gated test module is a broad, simple integration smoke suite for Swift helper modules. It validates that encryption, sync, static large objects, TempURL, versioning, symlink detection, rate-limit parsing, quota structs, conflict resolution, and retry scheduling can all be used from one test crate.

## Important APIs, types, and functions

- `encryption::EncryptionConfig::new`, `encrypt_data`, and `EncryptionMetadata::to_headers` are checked for metadata generation and coexistence with user metadata.
- `sync::SyncConfig::from_metadata`, `generate_sync_signature`, `verify_sync_signature`, `resolve_conflict`, and `SyncQueueEntry` retry methods are exercised.
- `slo::SLOManifest`, `SLOSegment`, `calculate_etag`, and `total_size` are validated structurally.
- `tempurl::TempURL::new` and `generate_signature` must produce a 40-character HMAC-SHA1 hex signature.
- `versioning::generate_version_name` must include the original object names and vary across object inputs.
- `symlink::is_symlink` is called against metadata using `x-symlink-target`, which is not the canonical request metadata key used by `symlink.rs`.
- `ratelimit::RateLimit::parse` and `quota::QuotaConfig` are checked.

## Control flow

The tests are independent. They construct small domain values, call one or two helpers, and assert stable properties such as header values, deterministic signatures, signature length, SLO size, version-name inclusion, rate-limit numeric fields, quota fields, conflict decisions, and retry timestamps. No async runtime, HTTP server, or object storage is involved.

## State and persistence behavior

All state is local to the tests. Encryption produces ciphertext and metadata but does not persist keys. Sync retry state is held in a `SyncQueueEntry`, where `schedule_retry(2000)` increments `retry_count` and sets `next_retry` to `2060`. User metadata coexistence is represented by merging encryption headers with an object metadata key.

## Dependencies and integration points

This file depends on the public Swift helper modules exported by `rustfs_protocols`. The modules themselves integrate with cryptographic crates, HMAC signing conventions, Swift container-sync metadata headers, SLO manifest formats, and quota/rate-limit metadata contracts. The test suite verifies helper interoperability at the API level.

## Risks and edge cases

- The symlink detection test uses `x-symlink-target`, while the symlink implementation checks `x-object-symlink-target`; the test intentionally ignores the result, so it does not assert the canonical behavior.
- Encryption is not round-tripped with `decrypt_data`.
- SLO ETag coverage checks only a one-segment manifest and non-empty digest, not multi-segment ordering semantics.
- TempURL and sync signatures check length and determinism but not known test vectors.
- Versioning checks inclusion and inequality but not sort order or timestamp format; the dedicated versioning test file covers those.

## Test signals

This module is useful as a compilation and basic behavior canary across many Swift Phase 4 helpers. It can catch public API removals, major metadata-format changes, and simple regression in deterministic signing or retry math. It is not a substitute for storage-backed Swift API tests.
