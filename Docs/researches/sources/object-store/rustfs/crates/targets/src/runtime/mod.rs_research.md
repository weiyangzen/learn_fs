# sources/object-store/rustfs/crates/targets/src/runtime/mod.rs

## Purpose
Core runtime lifecycle and replay machinery for instantiated targets. It manages active target references, runtime status/health snapshots, replay worker cancellation, target activation, and durable queue replay.

## Important APIs, types, and functions
- Public submodules: `adapter`, `ops_diagnostics`, `s3_hooks`, `sidecar`, `sidecar_protocol`, and `tls`.
- `SharedTarget<E>` is the shared `Arc<dyn Target<E>>` runtime object.
- `ReplayWorkerManager` stores cancel senders and can snapshot or stop all workers.
- Snapshot types: `RuntimeActivation`, `RuntimeStatusSnapshot`, `RuntimeTargetSnapshot`, `RuntimeTargetHealthState`, and `RuntimeTargetHealthSnapshot`.
- `ReplayEvent` reports delivered, retryable, dropped, permanent, exhausted, and unreadable replay outcomes.
- `TargetRuntimeManager` provides add/get/remove/close/list/snapshot/health methods.
- `init_target_and_optionally_start_replay`, `activate_targets_with_replay`, and `start_replay_worker` implement activation and queue replay.

## Control flow
Activation initializes each target. Init failure drops non-store targets but keeps store-backed targets so replay can still be attempted. Enabled store-backed targets get replay workers; disabled targets are kept without replay. Replay loops list store keys, confirm raw entries are readable, batch keys, and send them from store. `NotConnected` and `Timeout` retry with exponential backoff and jitter up to five attempts; `Dropped` and other errors produce terminal events.

## State and persistence behavior
Runtime manager state is an in-memory map keyed by `TargetID` string. Replay workers operate on target-provided durable stores and remove/retain entries according to target `send_from_store` behavior. The runtime itself only tracks cancellation channels, active target references, and delivery/health snapshots.

## Dependencies and integration points
It depends on target traits, target IDs, store traits and queue payloads, `TargetDeliverySnapshot`, `TargetError`, `StoreError`, serde bounds, `tokio` channels/semaphores, and tracing. `adapter.rs` wraps these primitives for plugin/runtime consumers.

## Risks and edge cases
Replay currently processes a batch whenever it has any key, making the batch timeout mostly relevant when keys are pending but no new store keys arrive. `1u32 << retry_count` is safe for the current small retry bound but would need care if retry counts grow. Store `list()` order and target send semantics determine replay ordering and deletion behavior. Cancel checks are cooperative, so a worker may finish a batch before stopping.

## Test signals
Tests verify `remove_and_close` removes a target and calls close once, and snapshots contain target id/type data. Adapter tests provide additional coverage for activation and replay-worker lifecycle.
