# sources/object-store/rustfs/crates/notify/src/runtime_view.rs

## Purpose
Provides read-only views of runtime targets, per-target metrics, target health, and combined runtime/replay status.

## Important APIs, types, and functions
- `NotifyRuntimeView` holds shared target list and replay worker manager.
- `get_active_targets`, `get_all_targets`, and `get_target_values` expose runtime target IDs/handles.
- `snapshot_target_metrics` converts target runtime snapshots into `NotificationTargetMetricSnapshot`.
- `snapshot_target_health` returns `RuntimeTargetHealthSnapshot` values.
- `runtime_status_snapshot` combines target runtime and replay worker status.

## Control flow
Each method reads the relevant lock and delegates to `TargetList`/target runtime methods. Status snapshot reads replay workers and target list together.

## State and persistence behavior
No mutation. It observes in-memory target runtime state and replay workers. Target queue lengths and delivery counts come from target runtime snapshots.

## Dependencies and integration points
Used by `NotificationSystem` facade and runtime facade tests. Depends on `TargetList`, `ReplayWorkerManager`, `TargetID`, `SharedTarget<Event>`, and rustfs-targets runtime snapshot types.

## Risks and edge cases
`get_active_targets` currently returns all target IDs in the runtime list; disabled/inactive health is visible only through health snapshots. Snapshot order follows target runtime ordering and should not be assumed unless the runtime manager guarantees sorting.

## Test signals
Tests cover empty queries/snapshots and a non-empty runtime with online and disabled targets, asserting target IDs, delivery metrics, health state, and runtime status counts.
