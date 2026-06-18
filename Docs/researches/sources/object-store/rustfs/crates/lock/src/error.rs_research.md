# sources/object-store/rustfs/crates/lock/src/error.rs

## Purpose
Defines the lock crate's error taxonomy, retry/fatal classification, conversions, and `Result<T>` alias.

## Important APIs, Types, And Functions
`LockError` variants include timeout, resource not found, permission denied, network, internal, already locked, invalid handle, configuration, serialization, deserialization, insufficient nodes, quorum not reached, queue full, and not owner. Constructor helpers mirror the variants. `is_retryable` marks timeout/network/internal errors; `is_fatal` marks not-found/permission/configuration. Manual `Clone` recreates source-carrying errors with synthetic `io::Error`s.

## Control Flow
Conversions map I/O kinds, serde JSON categories, and tonic status codes into `LockError`. Classification helpers are used by callers to decide retry or escalation policy.

## State And Persistence
No state. Error values may carry `LockId` and durations. Source errors are boxed and not faithfully preserved across `Clone`.

## Dependencies And Integration
Uses `thiserror`, `tonic`, `serde_json`, and crate `LockId`. Distributed lock acquisition emits `QuorumNotReached`; client and fast-lock layers can use the other variants.

## Risks And Edge Cases
`std::io::ErrorKind::TimedOut` maps to `Internal` rather than `Timeout`, though `is_retryable` still treats it as retryable. `tonic::DeadlineExceeded` also maps to `Internal`, which may make user-facing errors less precise. Cloned network/serde errors lose original source type.

## Test Signals
Tests cover constructor output shapes, retryable classification, and fatal classification.
