# sources/object-store/rustfs/crates/kms/src/lib.rs

## Purpose
Defines the public crate boundary for RustFS KMS, documents the KMS architecture, and re-exports API types, configuration, errors, manager/service types, and core KMS types.

## Important APIs, Types, And Functions
Public modules include `api_types`, `backends`, `config`, `manager`, `service`, `service_manager`, and `types`; `cache`, `encryption`, `error`, and `time_serde` are internal. Public re-exports include configuration, `KmsError`, `KmsManager`, `ObjectEncryptionService`, `DataKey`, service manager functions, status, and API request/response DTOs. Backward-compatible functions include deprecated `init_global_services`, `shutdown_global_services`, and current `is_encryption_service_healthy`.

## Control Flow
The only runtime logic delegates global health checks to `get_global_encryption_service` and then to `ObjectEncryptionService::health_check`. Deprecated global init/shutdown are no-ops/logging placeholders because dynamic service management moved to `KmsServiceManager`.

## State And Persistence
Global state is owned by `service_manager.rs`; this file exposes accessors but does not store it directly.

## Dependencies And Integration
This is the integration surface consumed by other RustFS crates. The documentation explicitly states the master key -> DEK -> object data hierarchy and warns that generated DEKs must not be cached by key id alone.

## Risks And Edge Cases
Deprecated no-op functions may mislead legacy callers into thinking a passed `ObjectEncryptionService` was globally installed. The `#![deny(clippy::unwrap_used)]` lint raises quality for this crate, but tests still use `expect`, which is acceptable.

## Test Signals
Tests cover global service lifecycle, versioned reconfiguration preserving old `Arc` service references while new calls use a new version, and serialization of concurrent reconfiguration through the service manager mutex.
