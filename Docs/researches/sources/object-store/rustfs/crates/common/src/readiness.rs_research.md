# sources/object-store/rustfs/crates/common/src/readiness.rs

## Purpose
Provides a tiny atomic readiness state machine for process startup, separating boot, storage readiness, IAM readiness, and full serving readiness.

## Important APIs, types, and functions
`SystemStage` is a `repr(u8)` enum with `Booting`, `StorageReady`, `IamReady`, and `FullReady`. `GlobalReadiness` wraps an `AtomicU8` and exposes `new`, `mark_stage`, `is_ready`, and `current_stage`.

## Control flow
`new` initializes the status to `Booting`. Components call `mark_stage`, which uses `fetch_max` to advance monotonically. Readers call `is_ready` for a strict full-ready check or `current_stage` for the decoded stage.

## State and persistence behavior
The only state is an in-memory atomic byte. `SeqCst` ordering is used for both updates and reads. State cannot regress through the public API, and invalid raw values fall back to `Booting` after a debug assertion.

## Dependencies and integration points
The file only depends on the standard atomic library. Higher-level readiness/liveness handlers can share a `GlobalReadiness` to gate traffic while storage and IAM caches initialize.

## Risks and edge cases
The monotonic `fetch_max` model cannot represent a later loss of readiness. `is_ready` only returns true for exactly `FullReady`, so future enum variants would need explicit handling. There is no global singleton here; integration code must decide ownership.

## Test signals
Tests cover the initial state, normal progression, no regression after full readiness, concurrent marking from threads, and `is_ready` returning true only at `FullReady`.
