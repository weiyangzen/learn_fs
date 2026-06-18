# sources/object-store/rustfs/crates/concurrency/src/deadlock.rs

## Purpose
Provides the concurrency-layer deadlock manager and lightweight request tracker around `rustfs-io-core` deadlock detection.

## Important APIs, types, and functions
`DeadlockMonitorPolicy` carries enablement, check interval, and hang threshold with `to_core_config`. `DeadlockManager` owns the policy, `Arc<CoreDeadlockDetector>`, and a Tokio mutex `running` flag. It exposes lifecycle, lock registration, request tracking, and `detect_deadlock`. `RequestTracker` records request metadata and lock resource names, forwarding acquire/release events to the core detector.

## Control flow
`from_policy` creates the core detector. `start` is no-op when disabled and otherwise idempotently flips `running` while logging lifecycle state. `track_request` registers a request with placeholder thread id `1`; tracker methods record lock acquire/release, and `Drop` unregisters the request.

## State and persistence behavior
All state is in memory inside the core detector, the manager running flag, and tracker-local resource map. There is no background loop implemented here despite the lifecycle naming.

## Dependencies and integration points
Integrates `rustfs_io_core::{DeadlockDetector, DeadlockDetectorConfig, LockType}`, `rustfs_io_metrics::deadlock_metrics`, Tokio mutexes, and `tracing`. Richer request-resource diagnostics are explicitly delegated to `rustfs::storage::deadlock_detector::RequestResourceTracker`.

## Risks and edge cases
The placeholder thread id means all acquisitions are attributed to one logical thread unless the core detector treats it abstractly. `start` logs but does not spawn periodic checks. `record_lock_acquire` always records lock type label `"read"` to metrics regardless of actual lock type. Consumers must call `record_lock_release` correctly.

## Test signals
Tests cover disabled manager creation, policy-to-core conversion, request tracking, lock registration, acquisition recording, and resource map visibility.
