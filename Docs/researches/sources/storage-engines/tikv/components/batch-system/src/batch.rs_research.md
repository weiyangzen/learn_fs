# sources/storage-engines/tikv/components/batch-system/src/batch.rs

## Purpose
Core implementation of TiKV's generic batch FSM executor. It batches normal FSMs and an optional control FSM, dispatches them to `PollHandler` hooks, reschedules hot or priority-mismatched FSMs, and owns worker thread lifecycle.

## APIs, Types, And Functions
`FsmTypes` unifies normal/control/shutdown messages. `Batch` stores current polling work. `HandleResult` lets handlers continue or stop after a message progress count. `PollHandler` defines lifecycle hooks: `begin`, `handle_control`, `handle_normal`, `light_end`, `end`, and `pause`. `Poller::poll` is the main loop. `HandlerBuilder`, `BatchSystem`, `PoolState`, `BatchRouter`, and `create_system` form the public construction and execution surface.

## Control Flow
Pollers fetch from resource-control channels. If no work exists they call `pause` and block. Each round invokes `begin`, handles control first, handles existing normal FSMs, opportunistically pulls more normals up to batch size, calls `light_end`, schedules skipped FSMs, calls `end`, records metrics, and releases/removes/reschedules FSMs. Hot FSMs are periodically rescheduled to redistribute load, and priority mismatches move FSMs to the proper normal/low-priority queue.

## State And Persistence
State is entirely in memory: batch slots, scheduler channels, worker handles, joinable worker IDs, per-FSM metrics collectors, and optional `PoolStateBuilder`. There is no durable persistence. Ownership of FSMs moves between mailboxes and pollers, and shutdown sends `FsmTypes::Empty` sentinels.

## Dependencies And Integration Points
Uses `resource_control::channel`, TiKV threading utilities, metrics from `metrics.rs`, scheduler types, mailbox ownership, file-system I/O type labeling, failpoints, and online `Config` updates. Higher-level TiKV systems plug in concrete normal/control FSMs and handlers.

## Risks And Test Signals
High-risk areas are ownership release/removal correctness, starvation under hot FSMs, shutdown races, and handler contracts around `StopAt` progress. Tests and benches cover basic execution, priorities, resource-group scheduling, and benchmark fairness/load patterns. Metrics provide production signals for schedule wait, poll duration, rounds, counts, and reschedules.
