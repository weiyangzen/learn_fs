# sources/object-store/rustfs/crates/notify/src/integration.rs

## Purpose
Defines the high-level `NotificationSystem` facade and aggregate notification metrics. It wires together notifier dispatch, target registry, config management, bucket rule management, live event pipeline, runtime views, health/status snapshots, and shutdown behavior.

## Important APIs, types, and functions
- `LiveEventBatch` returns recent live events with a cursor (`next_sequence`) and truncation flag.
- `NotificationMetrics` tracks processing, processed, failed, skipped counts, and uptime through atomics.
- `NotificationMetricSnapshot` and `NotificationTargetMetricSnapshot` are exported metric DTOs.
- `NotificationSystem::new` builds all shared components and `NotifyServices`.
- Facade methods expose target queries, subscriber checks, live event subscription/history, target/bucket config mutation, reload, event sending, status, target metrics/health, runtime status, and shutdown.
- `load_config_from_file` reads and unmarshals a server `Config` then reloads the system.

## Control flow
Construction creates a broadcast channel, metrics, subscriber view, rule engine, notifier, registry, shared config, replay worker manager, stream concurrency semaphore, and live event history, then assembles `NotifyServices`. `init` delegates to config manager initialization. `send_event` routes through `NotifyPipeline`, which records/broadcasts live events before target dispatch. `Drop` logs a metrics/status snapshot and emits final metric values through the `metrics` crate.

## State and persistence behavior
Runtime state is held in shared Arcs: target list, config lock, rule engine map, subscriber index, replay workers, live event history, and metric counters. Persistent target config writes are delegated to `NotifyConfigManager`. Bucket notification config lives in memory via rule engine and subscriber snapshot; this file does not persist bucket XML by itself.

## Dependencies and integration points
Integrates `EventNotifier`, `TargetRegistry`, `NotifyServices`, `LiveEventHistory`, `BucketNotificationConfig`, target replay workers, `metrics`, `tokio` sync primitives, `rustfs_config`, and `rustfs_targets` runtime snapshots.

## Risks and edge cases
Metric counters use relaxed atomics and `fetch_sub` on processing counts; incorrect caller pairing of increment/decrement could underflow in debug or wrap in release. `Drop` cannot await async shutdown, so callers should explicitly call `shutdown` for target/replay cleanup. Live event history is bounded and can truncate client catch-up responses.

## Test signals
Tests cover live event history cursor/truncation behavior and confirm `NotificationSystem` exposes live event listeners, records sent live events, and returns recent event batches.
