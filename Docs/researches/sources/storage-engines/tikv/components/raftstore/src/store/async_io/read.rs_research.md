# sources/storage-engines/tikv/components/raftstore/src/store/async_io/read.rs

Purpose: Implements the async read-side worker for raftstore: fetching raft log entries from the raft engine and generating tablet snapshots from a tablet engine checkpoint.

Important APIs and types: `ReadTask<EK>` has `FetchLogs` and `GenTabletSnapshot` variants. `FetchedLogs` returns a `GetEntriesContext` plus boxed `RaftlogFetchResult`. `GenSnapRes` is `Option<Box<(Snapshot, u64)>>`, carrying a generated raft snapshot and target peer. `AsyncReadNotifier` reports fetched logs and generated snapshots back to raftstore. `ReadRunner<EK, ER, N>` owns the notifier, raft engine, optional `TabletSnapManager`, and engine phantom.

Control flow: `Runnable::run` matches on `ReadTask`. For `FetchLogs`, it marks replication I/O, fetches `[low, high)` entries from the raft engine into a bounded vector, computes whether the size limit was hit, and notifies with success or converted error. For `GenTabletSnapshot`, it checks cancellation, marks load-balance or replication I/O, asserts the region is not tombstone, builds raft snapshot metadata and `RaftSnapshotData`, computes a `TabletSnapKey`, checkpoints the tablet into the snapshot manager path, registers the snapshot, updates metrics, and notifies success or failure.

State and persistence: Fetching logs is read-only. Snapshot generation creates or replaces a checkpoint directory under the tablet snapshot manager's generation path, potentially deleting an old checkpoint with encryption-aware trash removal. Snapshot metadata persists region, version, removed records, merged records, term, index, conf state, and `for_balance`.

Dependencies and integration points: It depends on `KvEngine` checkpointers, `RaftEngine::fetch_entries_to`, raft protobuf snapshots, `TabletSnapManager`, snapshot metrics, failpoints, file-system I/O type guards, and raftstore worker `Runnable`. Notifications return results to the peer/store FSM that requested log fetch or snapshot generation.

Risks: `snap_mgr()` unwraps, so callers must call `set_snap_mgr` before `GenTabletSnapshot`. Checkpoint creation errors are logged and reported as `None`; callers must interpret missing snapshot results. Cancellation is checked only before expensive work starts, not during checkpoint creation. Snapshot data serialization uses `unwrap`, assuming protobuf serialization cannot fail.

Test signals: No local tests. Coverage is expected from snapshot generation, raft log fetch, and raftstore integration tests using async read workers and failpoints.
