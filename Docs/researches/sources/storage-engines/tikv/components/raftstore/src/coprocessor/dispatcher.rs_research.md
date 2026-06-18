# sources/storage-engines/tikv/components/raftstore/src/coprocessor/dispatcher.rs

## Purpose
`dispatcher.rs` is the raftstore coprocessor dispatch layer. It owns the observer registry, boxed cloneable observer wrappers, registration ordering, and the public `CoprocessorHost` hook methods that raftstore calls while proposing, applying, executing, persisting, splitting, snapshotting, computing consistency hashes, handling messages, and observing write batches.

## Important APIs, Types, And Functions
`StoreHandle` is the scheduling interface observers use to send raftstore side effects back into the store: approximate size/key updates, split requests, bucket refreshes, consistency hash results, and compaction-declined byte updates. The `SyncSender<SchedTask>` implementation is intentionally best-effort via `try_send`.

`SchedTask` is the concrete message enum emitted by split checkers and other coprocessors. `Registry<E>` stores observer vectors by hook family, each as `Entry { priority, observer }`, plus singleton `write_batch_observer` and `snapshot_observer`. The `impl_box_observer!` and `impl_box_observer_g!` macros adapt cloneable concrete observers into trait-object boxes.

`CoprocessorHost<E>` is the main facade. `new` installs default split checkers in priority order: `HalfCheckObserver`, `SizeCheckObserver`, `KeysCheckObserver`, `TableCheckObserver`, plus `SplitObserver` for admin split validation.

## Control Flow
Registration calls `start()` and then sorts ascending by priority; lower priority value runs earlier. `loop_ob!` and `try_loop_ob!` create an `ObserverContext`, invoke each observer, and stop when `ctx.bypass` is set. Error-returning hooks short-circuit on `Result::Err`.

The host dispatches query versus admin paths in `pre_propose`, `pre_apply`, `post_apply`, `pre_exec`, and `post_exec`. Snapshot hooks fan out through `apply_snapshot_observers`. Split checks are created through `new_split_checker_host`, which gives observers a chance to add checkers. Consistency checks walk observers, consuming portions of request context as each observer computes a hash. Apply command batch flushing first emits `post_apply` for contained commands and then lets command observers inspect or mutate the batch vector.

## State And Persistence Behavior
The dispatcher itself persists no data. Persistence influence is indirect: `post_exec_*` can request special persistence, `pre_persist` can veto region/meta persistence, `pre_write_apply_state` can veto apply-state writes, and write-batch/snapshot observers can observe engine writes or snapshots. `StoreHandle` messages cross back into raftstore state machines asynchronously and can be dropped if the sync channel is full.

## Dependencies And Integration Points
This file integrates `engine_traits`, `kvproto`, `raft`, split-check modules, read/write observers, consistency checks, and raftstore store types (`BucketRange`, `SnapKey`, `Snapshot`). It is called by raftstore FSM/apply code and is extended by CDC, resolved-ts, PiTR, region-info access, split observers, and consistency observers.

## Risks
Priority ordering is contract-sensitive; a lower numeric priority runs first. `try_send` silently drops scheduling tasks on channel pressure, so callers must tolerate stale approximate stats or delayed split signals. Singleton write-batch and snapshot observers mean later registrations replace earlier ones. Several hooks run on performance-critical raftstore paths, so observer code must avoid blocking. `on_update_safe_ts` checks `query_observers.is_empty()` before iterating `update_safe_ts_observers`, which is surprising and could suppress safe-ts hooks if no query observer is registered.

## Test Signals
Unit tests verify correct hook routing, priority ordering, bypass behavior, error short-circuiting, apply snapshot hooks, persistence hooks, raft message hooks, and command-batch flushing through a synthetic `TestCoprocessor`.
