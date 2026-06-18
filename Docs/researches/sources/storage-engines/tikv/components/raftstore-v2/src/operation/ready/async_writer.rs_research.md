# sources/storage-engines/tikv/components/raftstore-v2/src/operation/ready/async_writer.rs

## Purpose
Wraps asynchronous raft ready persistence for a peer. It tracks which ready numbers are not yet persisted, merges ready tasks that have no durable data into preceding writes, and releases persisted raft messages only after their durability dependency is satisfied.

## Important APIs, Types, And Functions
`UnpersistedReady` records ready number, maximum following empty ready number, persisted-message batches, snapshot presence, and flushed epoch. `AsyncWriter::new`, `write`, `known_largest_number`, `send`, `merge`, `on_persisted`, `persisted_number`, and `all_ready_persisted` implement the writer. Test-export methods `subscribe_flush` and `notify_flush` support waiting for flush. The file also implements `WriteRouterContext` for `StoreContext` and `PersistedNotifier` for `StoreRouter`.

## Control Flow
`write` sends tasks with durable data to the write router and records an `UnpersistedReady`. Empty tasks are either returned immediately when no prior ready is pending, or merged into the last unpersisted ready by extending `max_empty_number` and buffering any messages. `on_persisted` pops unpersisted readies up to the completed ready number, accumulates deferred raft messages, captures the last flushed epoch and snapshot flag, advances `persisted_number` to include merged empty readies, and asks the write router to check newly persisted work.

## State And Persistence Behavior
The durable writes are executed by the write router and write workers outside this file. `AsyncWriter` maintains only in-memory ordering state, but it is safety-critical because persisted messages must not be sent before the entries or state they depend on are durable. Snapshot and flushed-epoch flags are carried forward to ready completion handling.

## Dependencies And Integration Points
Depends on `WriteRouter`, `WriteTask`, write senders, store config/metrics, persisted notifier callbacks, `PeerMsg::Persisted`, raft messages, and ready handling in `ready/mod.rs`.

## Risks And Edge Cases
Ready numbers must be monotonic and persisted callbacks must match queued readies; otherwise the code panics through `slog_panic`. Empty ready merging must preserve deferred message ordering and include snapshots/flushed epochs from prior persisted work. Persisted notifications are best effort through router `force_send`; failures are logged.

## Test Signals
No local unit tests are present in this file. Signals include ready-number panic paths, persisted message ordering in integration tests, test-export flush channels, and ready persistence metrics from the write router.
