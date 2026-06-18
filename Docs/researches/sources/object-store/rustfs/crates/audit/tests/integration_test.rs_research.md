# sources/object-store/rustfs/crates/audit/tests/integration_test.rs

## Purpose
This integration test file exercises basic audit crate construction and parsing paths through public APIs. It verifies that `AuditSystem` and `AuditRegistry` can be created, that webhook config/env target creation does not require server storage in the covered cases, and that event/enable parsing conventions behave as expected.

## Important APIs, Types, and Functions
Tests use `rustfs_audit::*`, `AuditSystem::new`, `AuditRegistry::new`, `AuditRegistry::create_audit_targets_from_config`, `rustfs_config::server_config::{Config, KVS}`, `temp_env::with_vars`, and `rustfs_targets::EventName`. They construct `audit_webhook` config sections with `_` defaults and named `primary` instances.

## Control Flow
Async tests create empty or webhook-populated configs and call registry/system methods. The env-only test sets `RUSTFS_AUDIT_WEBHOOK_ENABLE_PRIMARY` and `RUSTFS_AUDIT_WEBHOOK_ENDPOINT_PRIMARY`, builds a single-thread Tokio runtime, and invokes target creation from an empty file config. Event parsing tests parse and expand S3 event names. Enable parsing tests lower-case strings and match truthy values.

## State and Persistence Behavior
State is temporary, except environment variables are scoped by `temp_env`. No target data is persisted. The tests intentionally avoid requiring server storage for basic target creation paths.

## Dependencies and Integration Points
These tests are cross-crate integration signals between audit, config, target event parsing, and environment-variable parsing. They are relevant to `AuditRegistry::create_audit_targets_from_config` and public audit initialization behavior.

## Risks and Edge Cases
The env-only test relies on process environment isolation from `temp_env`; parallel tests that use the same variables could interfere if not properly isolated. Assertions mostly check `is_ok` rather than inspecting produced targets, so they catch gross parser failures but not detailed target configuration regressions. Truthy enable parsing treats invalid values as false.

## Test Signals
The tests confirm initial `AuditSystem` state is `Stopped`, new registries are empty, webhook config/env parsing can succeed without initialized server storage for these paths, event names parse/expand/mask, and enable strings `1/on/true/yes` are truthy while `0/off/false/no/invalid` are false.
