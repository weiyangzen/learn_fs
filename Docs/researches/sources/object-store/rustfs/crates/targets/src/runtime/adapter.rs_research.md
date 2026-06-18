# sources/object-store/rustfs/crates/targets/src/runtime/adapter.rs

## Purpose
Defines the runtime adapter abstraction for target plugins and implements the builtin in-process adapter. The adapter isolates activation, replay-worker management, runtime replacement, snapshots, health checks, and shutdown behind a stable trait.

## Important APIs, types, and functions
- `PluginRuntimeAdapter<E>` trait defines `activate_with_replay`, `replace_runtime_targets`, `stop_replay_workers`, `snapshot_runtime_status`, `snapshot_runtime_health`, and `shutdown`.
- `BuiltinPluginRuntimeAdapter<E>` stores replay hook, replay-start observer, optional replay semaphore, batch timeout, idle sleep, and stop log prefix.
- `BuiltinPluginRuntimeAdapter::new` configures those runtime parameters.

## Control flow
Activation wraps `activate_targets_with_replay` and, for each target, calls `init_target_and_optionally_start_replay`. Store-backed enabled targets can start replay workers through `start_replay_worker`. Replacement stops old replay workers, closes existing runtime targets, adds activated targets, and swaps replay worker managers. Shutdown is the same stop-and-close sequence without adding replacements.

## State and persistence behavior
The adapter holds runtime policy/configuration in memory. It does not persist target state but controls replay workers that drain persistent target stores. Store-backed targets can remain active even when initialization fails so queued payloads can still be replayed.

## Dependencies and integration points
It depends on `runtime/mod.rs` primitives, `Target`, `TargetError`, async trait support, serde bounds, `tokio::sync::Semaphore`, and configured replay hooks supplied by callers. `plugin.rs` uses it through the trait when creating runtime activations from config.

## Risks and edge cases
Replacement stops and closes the old runtime before adding new activated targets, so partial activation decisions are already baked in. Failed target close operations are logged inside runtime manager cleanup and do not abort shutdown. Replay concurrency depends on the optional semaphore supplied by the caller.

## Test signals
Tests cover empty activation, non-store targets being skipped on init failure, store-backed targets being retained with a replay worker after init failure, and shutdown clearing runtime targets/replay workers while calling target close exactly once.
