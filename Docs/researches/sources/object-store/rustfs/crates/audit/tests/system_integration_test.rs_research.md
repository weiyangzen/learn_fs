# sources/object-store/rustfs/crates/audit/tests/system_integration_test.rs

## Purpose
This file contains broader integration tests for the audit system lifecycle, metrics wiring, no-target dispatch, global audit functions, multi-instance config parsing, target type constants, concurrent state reads, and concurrent dispatch under load.

## Important APIs, Types, and Functions
Tests use `rustfs_audit::*`, `AuditSystem`, global functions such as `init_audit_system`, `dispatch_audit_log`, `is_audit_system_running`, `AuditLogger::instance`, `AuditLogger::is_enabled`, and `AuditLogger::log`. Helpers construct representative `AuditEntry` values with `ApiDetails`, headers, tags, request metadata, and `EventName::ObjectCreatedPut`.

## Control Flow
Lifecycle tests start with empty config and accept either storage-unavailable failure or success that leaves state `Stopped`. Metrics tests reset metrics, start the system, then assert system-start count increments and validation values are nonnegative. No-target dispatch accepts either success or `NotInitialized`. Global audit function tests ensure logging APIs do not panic when the system is not running. Multi-instance config creates default, primary, and secondary webhook entries and tolerates expected storage failure after parsing. Concurrent tests spawn ten state readers and one hundred dispatch tasks.

## State and Persistence Behavior
The system is in-memory. Global audit functions may touch singleton/global audit logger state. Config KVS maps are local. No real network or storage target is required.

## Dependencies and Integration Points
This file exercises public audit crate exports and their interaction with `rustfs_config`, `rustfs_targets::TargetType`, and global logger infrastructure. It is a consumer-facing safety net for API behavior under uninitialized/no-target conditions.

## Risks and Edge Cases
Several tests allow multiple outcomes to accommodate test environments without server storage, so they may miss detailed regressions. Global singleton state can cause ordering sensitivity if tests are run concurrently. Concurrent dispatch tests only require completion and consistent accounting, not a specific success/error distribution.

## Test Signals
Signals include `Stopped` initial and empty-config states, `close` idempotence, metric recording on start attempts, global logging safety when disabled, distinct `audit_log` and `notify_event` target types, safe concurrent state reads, and 100 concurrent dispatch attempts completing within five seconds.
