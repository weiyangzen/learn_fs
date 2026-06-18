# sources/object-store/rustfs/crates/protocols/tests/swift_phase4_integration.rs

## Purpose

This Swift-feature-gated integration test module checks that Phase 4 Swift helper modules can be used together from the public `rustfs_protocols::swift::*` namespace. It is a lightweight cross-module smoke test rather than a storage-backed HTTP integration test.

## Important APIs, types, and functions

- Imports `rustfs_protocols::swift::*`, so the tests depend on the Swift module re-export surface.
- `symlink::is_symlink` and `symlink::get_symlink_target` are checked against metadata containing `x-object-symlink-target`.
- `expiration::parse_delete_at` parses a Unix timestamp string from `x-delete-at`.
- `ratelimit::RateLimiter::new`, `RateLimit { limit, window_seconds }`, and `check_rate_limit` are used to verify independent counters by key.
- `ratelimit::extract_rate_limit` parses account metadata from `x-account-meta-rate-limit` in `limit/window` format.

## Control flow

The first test is compile-only and exists to ensure the Phase 4 modules remain accessible. The symlink-expiration test builds one metadata map containing both a symlink target and an expiration timestamp, then verifies both modules can read their own headers without conflict. The rate-limit key test creates one limiter and applies the same policy to two keys in lockstep, verifying each key allows three requests and then rejects the fourth. The metadata extraction test parses `1000/60` into the expected limit and window.

## State and persistence behavior

There is no persisted state. The only mutable state is inside `RateLimiter`, which maintains in-memory per-key counters or token-bucket state for the life of the limiter instance. Metadata maps are local and demonstrate that Phase 4 features share object/account metadata by convention rather than through a central schema.

## Dependencies and integration points

The file depends on public Swift modules for symlink, expiration, and rate limiting. It integrates at the crate API level, confirming `rustfs_protocols::swift::*` exposes these helpers together under the `swift` feature. It does not instantiate the Swift HTTP handler or storage backend.

## Risks and edge cases

- The compile-only test has no assertions, so it only guards import viability.
- The rate-limit test assumes deterministic exhaustion after exactly `limit` successful calls with no refill during the test window.
- Expiration parsing uses a fixed future-like timestamp but does not validate expiration rejection, deletion scheduling, or clock behavior.
- Metadata coexistence is tested only for header key independence, not for handler serialization, persistence, or case normalization.

## Test signals

The module signals that Phase 4 metadata features can coexist and that rate limiting is isolated by key. It should catch public API breakage in module names or basic function signatures. It does not provide end-to-end HTTP/storage confidence.
