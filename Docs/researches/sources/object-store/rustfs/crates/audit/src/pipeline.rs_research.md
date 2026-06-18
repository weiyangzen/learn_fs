# sources/object-store/rustfs/crates/audit/src/pipeline.rs

## Purpose

`pipeline.rs` dispatches audit entries to configured targets, exposes a runtime view for target management, and wraps `rustfs-targets` runtime/replay activation for hot reload and reliable delivery.

## Important APIs and Types

`AuditPipeline` owns an `Arc<Mutex<AuditRegistry>>`. `dispatch` fans one `AuditEntry` to all current targets. `dispatch_batch` sends multiple entries to every target. `snapshot_target_metrics` returns delivery counters, and `snapshot_target_health` asks the registry runtime manager for health snapshots.

`AuditRuntimeView` provides runtime target inspection and mutation helpers: `list_targets`, `get_target_values`, `get_target`, `enable_target`, `disable_target`, `remove_target`, and `upsert_target`. Enable/disable currently validate and log state changes; they do not toggle target behavior in the registry.

`AuditRuntimeFacade` owns the registry, replay worker manager, and a `PluginRuntimeAdapter<AuditEntry>`. It builds a `BuiltinPluginRuntimeAdapter` with replay-event callbacks, supports `replace_targets`, `shutdown_runtime`, `activate_targets_with_replay`, and `stop_replay_workers`.

## Control Flow

`dispatch` snapshots target values under the registry lock, releases the lock, converts the audit entry into `EntityTarget<AuditEntry>` for each target, and awaits all target `save` futures with `join_all`. It records per-target success/failure metrics and records one audit success only if all targets succeeded; partial failures are logged and counted as audit failure but still return `Ok(())`.

`dispatch_batch` similarly snapshots targets, then creates one async task per target that loops through all entries sequentially for that target. It logs individual target failures and a batch completion summary but does not currently update global audit event metrics.

Runtime replacement locks both registry and replay workers, then delegates activation/shutdown to the adapter. Replay callbacks log delivered, retryable, dropped, permanent failure, retry exhausted, and unreadable entry events, updating target success/failure metrics and final-failure counters where appropriate.

## State and Persistence

Pipeline state is shared registry access. Target state lives in target implementations and runtime manager snapshots; replay persistence is managed by `rustfs-targets` stores/workers rather than this file. The facade stores replay worker manager state behind an async `RwLock`.

## Dependencies and Integration Points

The file integrates with `AuditRegistry`, `AuditEntry`, `AuditError`, observability helpers, `rustfs_targets` target traits, runtime adapters, replay worker manager and replay events, Tokio locks, futures `join_all`, and structured tracing. It is the bridge between generated audit entities and external audit sinks.

## Risks and Edge Cases

Dispatch clones the full `AuditEntry` once per target; large headers/claims/tags amplify memory cost. Partial target failure is logged and recorded but not returned to callers, so callers cannot directly retry from `dispatch` errors. `dispatch_batch` does not record the same audit success/failure metrics as single dispatch. `enable_target` and `disable_target` are currently logging-only checks, which can mislead callers expecting active state changes. Holding registry locks across runtime replacement is necessary for consistency but can block target inspection or dispatch snapshots. Replay callback behavior must stay aligned with target retry semantics or metrics will drift.

## Test Signals

Tests should cover no-target no-op dispatch, all-target success, partial failure metrics/logging, batch dispatch success/error accounting, target metric snapshots, runtime view missing-target errors, upsert initialization failure and replacement behavior, remove target behavior, replay event metric updates, and hot-reload target replacement with replay workers.
