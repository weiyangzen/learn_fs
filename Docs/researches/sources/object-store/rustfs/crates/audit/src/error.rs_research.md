# sources/object-store/rustfs/crates/audit/src/error.rs

## Purpose

`error.rs` centralizes the audit crate error type and the `AuditResult<T>` alias used across initialization, configuration, target dispatch, persistence, serialization, I/O, and task joins.

## Important APIs and Types

`AuditResult<T>` is `Result<T, AuditError>`. `AuditError` derives `thiserror::Error` and includes configuration errors with optional source, missing config, target errors from `rustfs_targets`, not initialized/already initialized states, storage unavailability, save/load config source errors, serde JSON errors, std I/O errors, and Tokio join errors.

## Control Flow

The enum is used by `?` conversions for target, serialization, I/O, and join failures. Explicit variants are constructed by global/system/pipeline code for logical states such as missing targets or unavailable configuration.

## State and Persistence

No state or persistence exists in this file. It shapes how lower-level persistent or network failures are surfaced to callers.

## Dependencies and Integration Points

It integrates with `rustfs_targets::TargetError`, `serde_json::Error`, `std::io::Error`, `tokio::task::JoinError`, and `thiserror`. Public re-export from `lib.rs` makes these errors part of the crate API.

## Risks and Edge Cases

`Configuration(String, Option<Box<dyn Error + Send + Sync>>)` can carry rich source errors but is awkward to construct consistently. Some variants such as `ConfigNotLoaded`, `StorageNotAvailable`, `SaveConfig`, and `LoadConfig` may be used by neighboring modules not included in this subset; callers need to preserve source context when mapping errors. Target dispatch currently may log target failures without returning an aggregate error, so `AuditError::Target` does not necessarily mean all delivery failures bubble up.

## Test Signals

Tests should verify `From` conversions, display strings, source preservation for boxed errors, and API behavior where global operations intentionally return `Ok(())` when the audit system is not initialized.
