# sources/object-store/rustfs/crates/audit/src/registry.rs

## Purpose
`registry.rs` defines `AuditRegistry`, the audit crate's target registry and target factory facade. It owns a `TargetRuntimeManager<AuditEntry>` for live targets and a `TargetPluginRegistry<AuditEntry>` seeded with `builtin_target_plugins()`. Its role is to bridge RustFS audit configuration (`rustfs_config::server_config::Config` and `KVS`) to concrete `rustfs_targets::Target` implementations and to provide runtime target lookup, insertion, removal, and shutdown operations.

## Important APIs, Types, and Functions
`AuditRegistry::new` registers all built-in audit target plugins. `supports_target_type` and `create_target` expose plugin registry capabilities. `create_audit_targets_from_config` delegates bulk config/env parsing to `TargetPluginRegistry::create_targets_from_config(config, AUDIT_ROUTE_PREFIX)`, mapping `TargetError` into `AuditError`. Runtime APIs include `add_target`, `add_shared_target`, `remove_target`, `get_target`, `list_target_values`, `runtime_manager`, `runtime_manager_mut`, and `list_targets`. `close_all` removes and closes every live target, returning the first close error while still attempting all closes. `create_key` builds canonical `TargetID` strings from target type and target id. The older `enable_target`, `disable_target`, and `upsert_target` helpers create/check keys but only log state or insert into the runtime manager; actual enable/disable mutation is implemented by lower runtime abstractions in pipeline/runtime layers.

## Control Flow
Creation flow is plugin-driven: registered plugins interpret the audit config namespace and produce boxed `Target<AuditEntry>` values. Runtime mutation flow is manager-driven: boxed or shared targets are inserted into `TargetRuntimeManager`; removals call `remove_and_close`. Shutdown loops over a snapshot of keys, removes each target, awaits `close`, logs failed closes, and preserves only the first error for the return value.

## State and Persistence Behavior
State is in-memory only: plugin registrations and live target handles. Persistence, queues, and replay stores belong to target implementations and `rustfs_targets`. The registry does not persist target definitions itself. Debug assertions verify passed ids match target ids but are not runtime validation in release builds.

## Dependencies and Integration Points
The file depends on `rustfs_targets` for `TargetID`, target traits, shared target handles, plugin registry, runtime manager, and target errors. It depends on `rustfs_config` for the audit route prefix and config shape. It integrates upward with `AuditSystem`, `AuditRuntimeView`, `AuditRuntimeFacade`, and `AuditPipeline`, which wrap the registry behind locks.

## Risks and Edge Cases
`enable_target` and `disable_target` only check existence and log, so callers expecting state mutation must use runtime-layer APIs. `upsert_target` computes a key from separate type/id arguments but inserts the target under its own id via the manager, so mismatches are caught only by `debug_assert_eq!` in debug builds. `close_all` drains targets and returns the first close error; later errors are logged but not aggregated. Ordering depends on runtime manager key ordering.

## Test Signals
Unit tests assert that the AMQP factory is registered by default and that `close_all` calls close on both successful and failing targets, returns `AuditError::Target`, and clears registry contents. Integration tests exercise registry creation, config/env-only target creation, multiple webhook instance parsing, and fast empty-registry operations.
