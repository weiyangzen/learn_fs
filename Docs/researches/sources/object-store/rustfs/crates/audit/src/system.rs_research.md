# sources/object-store/rustfs/crates/audit/src/system.rs

## Purpose
`system.rs` defines `AuditSystem`, the high-level lifecycle manager for audit logging. It coordinates target registry access, system state, current configuration, replay worker cancellation, dispatch, reload, pause/resume, shutdown, runtime inspection, metrics, and performance validation.

## Important APIs, Types, and Functions
`AuditTargetMetricSnapshot` is a simple per-target metric DTO. `AuditSystemState` models `Stopped`, `Starting`, `Running`, `Paused`, and `Stopping`. `AuditSystem` stores `Arc<Mutex<AuditRegistry>>`, `Arc<RwLock<AuditSystemState>>`, `Arc<RwLock<Option<Config>>>`, and `Arc<RwLock<ReplayWorkerManager>>`. Public lifecycle methods are `start`, `pause`, `resume`, `close`, `reload_config`, `get_state`, and `is_running`. Dispatch APIs are `dispatch` and `dispatch_batch`. Target APIs include `enable_target`, `disable_target`, `remove_target`, `upsert_target`, `list_targets`, `get_target_values`, `get_target`, `snapshot_target_metrics`, `snapshot_target_health`, and `runtime_status_snapshot`. Observability APIs delegate to `observability::{get_metrics_report, validate_performance, reset_metrics}`.

## Control Flow
`start` rejects an already running system, tolerates concurrent starting with a warning, records metrics, stores the config, creates targets from config, sets `Starting`, and commits runtime targets to `Running`. `commit_runtime_targets` treats an empty target set as a stopped runtime: it clears current runtime targets and sets state to `Stopped`. Non-empty targets are activated through `AuditRuntimeFacade::activate_targets_with_replay` and swapped into the runtime via `replace_targets`. `dispatch` permits only `Running`, silently drops when `Paused`, and errors with `NotInitialized` otherwise. `dispatch_batch` is stricter and errors for any non-running state, including paused. `reload_config` stores the new config, records reload metrics, creates targets, and preserves `Paused` as the final state if the system was paused; otherwise the intended final state is `Running`, unless the target set is empty and `commit_runtime_targets` stops it. `close` transitions to `Stopping`, shuts down runtime targets and replay workers, clears config, logs stopped, and returns `Ok` even if shutdown logged an error.

## State and Persistence Behavior
All system state is in-memory and asynchronously locked. The saved config is a clone of the most recent config, including reload configs that stop the runtime. Replay worker state is held in `ReplayWorkerManager` and replaced or cleared with target runtime swaps. There is no direct disk persistence here; persistence is delegated to target queues/stores.

## Dependencies and Integration Points
The system depends on `AuditRegistry`, `AuditPipeline`, `AuditRuntimeFacade`, and `AuditRuntimeView`. It integrates with `rustfs_targets::ReplayWorkerManager` for replay lifecycle, `rustfs_config::Config` for target creation, and crate-level `observability` for metrics. It is the likely backend for global audit logger functions in the audit crate.

## Risks and Edge Cases
An empty config can make `start` return `Ok` but leave the system `Stopped`; tests document this as intended. `dispatch` and `dispatch_batch` have different paused behavior. `close` suppresses shutdown errors after logging, which simplifies callers but can hide partial close failures. `reload_config` writes the new config before target creation succeeds, so failed reloads can leave `config` reflecting a config that was not activated. Long target creation is done while holding the registry mutex because creation is called through a locked registry reference.

## Test Signals
The unit test `reload_with_empty_config_stops_existing_runtime` verifies that reload with empty config closes an existing target, clears replay workers, sets state to `Stopped`, and retains the new empty config. Integration/performance tests verify initial state, empty-config lifecycle, global metric increments, dispatch fast failure when stopped, concurrent state reads, and that close is idempotent for stopped systems.
