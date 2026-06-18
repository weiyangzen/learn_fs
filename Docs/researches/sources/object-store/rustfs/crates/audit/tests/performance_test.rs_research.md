# sources/object-store/rustfs/crates/audit/tests/performance_test.rs

## Purpose
This file provides synthetic performance and lifecycle checks for audit startup, target creation, dispatch, state transitions, registry operations, event mask/expansion helpers, and baseline throughput assumptions.

## Important APIs, Types, and Functions
Tests use `AuditSystem`, `AuditRegistry`, `AuditError`, `AuditEntry`, `ApiDetails`, `rustfs_targets::EventName`, Tokio `timeout`, and `Instant`. The main public methods covered are `start`, `close`, `dispatch`, `get_state`, `create_audit_targets_from_config`, `list_targets`, and `get_target`.

## Control Flow
Startup is timed with an empty config and must finish within five seconds. Target creation builds five webhook instances and allows either storage-related failure, other logged errors, or success, while still requiring completion within ten seconds. Dispatch builds a representative S3 `AuditEntry`; because empty config leaves the system stopped, dispatch must fail fast with `NotInitialized` in under 100 ms. Event mask and expansion helpers are called thousands of times and must stay under 100 ms. A synthetic 3000-event loop validates low CPU overhead relative to the 3k EPS/node target.

## State and Persistence Behavior
The tests use in-memory systems and configs only. No real target storage or network target is required. Cleanup calls `close` where applicable.

## Dependencies and Integration Points
This file connects audit performance expectations to `rustfs_targets::EventName`, config parsing, and the target registry. It also documents that actual EPS is expected to be constrained by network I/O rather than basic audit-entry construction or event helper logic.

## Risks and Edge Cases
Timing tests can be noisy in CI or under heavy load. Several tests print unexpected errors rather than failing, so they are coarse performance smoke tests rather than strict behavioral checks. The dispatch performance test intentionally depends on empty config leaving the system stopped; if lifecycle semantics change, this assertion must change.

## Test Signals
Expected signals are fast startup/close, fast target creation attempts, stopped state after empty-config start, fast dispatch failure when stopped, efficient event mask/expansion and empty registry operations, and synthetic core processing above 10k EPS with average latency below 1 ms.
