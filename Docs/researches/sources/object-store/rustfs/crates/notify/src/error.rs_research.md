# sources/object-store/rustfs/crates/notify/src/error.rs

## Purpose
Defines the notification crate's public error surface, separating lifecycle state failures from target, configuration, bucket-rule, storage, and I/O failures.

## Important APIs, types, and functions
- `LifecycleError` has `AlreadyInitialized` and `NotInitialized` variants for the global `OnceLock` lifecycle.
- `NotificationError` wraps `TargetError`, `LifecycleError`, `io::Error`, string-backed configuration/read/save/storage errors, ARN errors, target lookup errors, and initialization failures.
- `thiserror::Error` derives user-facing error messages and `#[from]` conversions for target and lifecycle errors.

## Control flow
The file has no runtime logic; it supplies variants consumed by global initialization, target registry/config managers, XML/bucket config handling, and runtime facade shutdown/replacement calls.

## State and persistence behavior
No state is stored here. Variants such as `ReadConfig`, `SaveConfig`, and `StorageNotAvailable` represent persistence failures emitted by `NotifyConfigManager`.

## Dependencies and integration points
Depends on `rustfs_targets::{TargetError, arn::TargetID}`, standard `io`, and `thiserror`. It is re-exported from `lib.rs`, making these errors part of the crate API.

## Risks and edge cases
Several variants carry plain strings, so downstream matching on error causes is less structured for configuration and storage failures. `Io(io::Error)` is not marked with `#[from]`, so conversions must be explicit where used.

## Test signals
There are no direct tests in this file; coverage is indirect through APIs returning `NotificationError`, especially global lifecycle tests, config manager tests, and runtime facade target replacement tests.
