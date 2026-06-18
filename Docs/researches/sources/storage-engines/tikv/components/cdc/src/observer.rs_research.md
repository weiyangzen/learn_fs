# sources/storage-engines/tikv/components/cdc/src/observer.rs

## Purpose
`observer.rs` implements `CdcObserver`, the raftstore coprocessor bridge that turns apply, role, and region-change callbacks into CDC endpoint tasks. It is the handoff point between raftstore event ordering and the CDC endpoint scheduler, and it also supplies the old-value callback used later while handling committed MVCC changes.

## Important APIs, Types, and Functions
- `CdcObserver::new` wires a FIFO `Scheduler<Task>` and shared `MemoryQuota`.
- `register_to` installs command, role, and region-change observers into `CoprocessorHost` with priorities chosen so CDC command observation precedes resolved-ts observation.
- `subscribe_region`, `unsubscribe_region`, and `is_subscribed` maintain `region_id -> ObserveId` under `RwLock`; unsubscribe checks the `ObserveId` to avoid ABA removal of a newer subscription.
- `CmdObserver::on_flush_applied_cmd_batch` filters `ObserveLevel::All` batches, creates a defensive engine snapshot, allocates batch memory quota, and schedules `Task::MultiBatch`.
- `RoleObserver::on_role_change` and `RegionChangeObserver::on_region_changed` schedule `Task::Deregister` with request errors when leadership is lost, a region is destroyed, split, or committed-merged.

## Control Flow
Apply callbacks assert a non-empty input batch, pass through failpoint `before_cdc_flush_apply`, then drop work unless all requested observation reaches `ObserveLevel::All`. A fake region wrapper is used to create a `RegionSnapshot` over the current engine snapshot so old values cannot disappear due to GC before CDC handles the batch. Role and region-change callbacks first check `observe_regions`; only subscribed regions generate deregistration tasks.

## State and Persistence Behavior
The observer holds only in-memory subscription state and does not persist CDC registrations. The engine snapshot captured for old-value lookup is a temporary consistency guard. Memory quota is charged with `alloc_force` before scheduling multi-batch work; endpoint-side processing is responsible for eventual release.

## Dependencies and Integration Points
The file depends on raftstore coprocessor traits, raft role metadata, TiKV storage `Statistics`, `MemoryQuota`, the CDC `endpoint::Task` protocol, and `old_value::get_old_value`. It is registered by CDC service setup and feeds endpoint delegate logic.

## Risks and Edge Cases
The shared `RwLock<HashMap<...>>` is called out as a potential bottleneck. Scheduler failure only logs warnings/errors after quota allocation, so downstream release behavior matters. Correct FIFO scheduler behavior is required by the file-level comment because apply events are strongly ordered.

## Test Signals
Unit tests cover command scheduling, memory quota charging, ignored events after observation handles stop, role-change NotLeader errors with leader and transferee peers, ABA-safe unsubscribe, no events for unsubscribed regions, and dropping txn extra when quota is exceeded.
