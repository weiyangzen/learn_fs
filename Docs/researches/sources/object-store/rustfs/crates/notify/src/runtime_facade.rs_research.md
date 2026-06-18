# sources/object-store/rustfs/crates/notify/src/runtime_facade.rs

## Purpose
Encapsulates target runtime activation, replay worker management, target replacement, and shutdown behind the generic `rustfs_targets` runtime adapter.

## Important APIs, types, and functions
- `NotifyRuntimeFacade` holds shared target list, replay worker manager, and a `PluginRuntimeAdapter<Event>`.
- `new` constructs a `BuiltinPluginRuntimeAdapter` with replay event callbacks, replay-start logging, concurrency limiting, poll/retry durations, and shutdown reason.
- `activate_targets_with_replay` initializes targets and replay workers.
- `replace_targets` commits a `RuntimeActivation` into target runtime and replay workers.
- `stop_replay_workers` and `shutdown` stop replay processing and close targets.

## Control flow
Activation is delegated to the runtime adapter. Replacement locks `replay_workers` before `target_list` and asks the adapter to replace runtime targets. Shutdown logs lifecycle state, observes active replay workers, locks in the same order, calls adapter shutdown, logs errors, sleeps briefly, and logs stopped.

## State and persistence behavior
Runtime facade manages in-memory target runtime state and replay worker handles. Replay workers may drain persisted target stores, but persistence is implemented by target/store types. Replay event callbacks update notification metrics and record final target failures for dropped/permanent/exhausted events.

## Dependencies and integration points
Uses `rustfs_targets::{BuiltinPluginRuntimeAdapter, PluginRuntimeAdapter, ReplayEvent, ReplayWorkerManager, RuntimeActivation, Target}`, notification metrics, `SharedNotifyTargetList`, semaphores, and tracing.

## Risks and edge cases
Lock ordering is explicitly documented as replay workers then target list; violating it elsewhere can deadlock. Shutdown is best-effort and logs adapter errors rather than returning them. Replay callback only increments processed for delivered events and failed for final failure classes; retryable/unreadable events do not change aggregate counters.

## Test signals
Tests verify empty replay worker stopping, empty activation, and replacement committing a runtime target visible through `NotifyRuntimeView` with no replay workers.
