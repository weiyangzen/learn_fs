# sources/storage-engines/tikv/components/backup-stream/src/observer.rs

## Purpose
`observer.rs` defines `BackupStreamObserver`, a raftstore coprocessor observer that watches apply, role, and region-change events and converts them into backup-stream endpoint tasks.

## Important APIs, types, and functions
- `BackupStreamObserver` stores the endpoint scheduler and an `Arc<RwLock<SegmentSet<Vec<u8>>>>` of task key ranges.
- `new` creates an observer for a scheduler.
- `register_to` installs command, role, and region-change observers into `CoprocessorHost` with fixed priorities.
- `should_register_region` checks whether a region overlaps registered task ranges, treating empty region end key as a synthetic infinity.
- `is_hibernating` returns true when no task ranges are registered.
- Implementations of `CmdObserver`, `RoleObserver`, and `RegionChangeObserver` schedule `Task::BatchEvent` or `Task::ModifyObserve` operations.

## Control flow
On command flush, only `ObserveLevel::All` batches are cloned and scheduled as `Task::BatchEvent`. When a region applies current term as leader and overlaps observed ranges, the observer schedules `ObserveOp::Start`. When a region leaves leadership and the observer is active, it schedules `ObserveOp::Stop`. Leader-side region destroy schedules `Destroy`; region update schedules `RefreshResolver`; create and bucket updates are ignored.

## State and persistence behavior
State is in-memory only: the observed task ranges are loaded by the endpoint from metadata. The observer does not persist data and does not directly manage subscriptions; it delegates all changes to the endpoint/region subscription manager through scheduled tasks.

## Dependencies and integration points
It integrates raftstore coprocessor traits, raft `StateRole`, `SegmentSet`, the backup-stream scheduler, `Task`, and `ObserveOp`. It is created by service wiring and owned by `Endpoint`.

## Risks and edge cases
- Command batches are cloned before scheduling; large batches have memory cost.
- Empty end key is approximated with 32 bytes of `0xff`, which is pragmatic but not a general infinity abstraction.
- If scheduler delivery fails, `try_send!` behavior determines whether events are only logged or dropped.
- Hibernation avoids noise when no tasks exist, but stale range state would suppress or admit observe operations incorrectly.

## Test signals
Tests validate observation cancellation through `ObserveHandle`, basic scheduling of start and batch events, ignoring non-overlapping regions and non-`All` observe levels, stopping on follower role changes, and hibernation suppressing role/region events.
