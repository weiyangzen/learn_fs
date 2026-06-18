# sources/storage-engines/tikv/components/raftstore/src/store/worker/cleanup_snapshot.rs

## Purpose
This worker garbage-collects idle raft snapshots and deletes specific snapshot files. It coordinates snapshot manager state with raft peer routing so peers can decide whether snapshots are still needed, while also handling disconnected peers by directly removing stranded snapshot files.

## Important APIs, Types, and Functions
- `Task::GcSnapshot` scans idle snapshots and schedules per-region GC.
- `Task::DeleteSnapshotFiles { key, snapshot, check_entry }` deletes a specific snapshot after ensuring metadata is loaded.
- `Runner<EK, ER>` stores `store_id`, `RaftRouter`, and `SnapManager`.
- `handle_snap_mgr_gc` groups idle snapshots by region and sends `CasualMessage::GcSnap`.
- `delete_snapshot` delegates to `SnapManager::delete_snapshot`.

## Control Flow
`GcSnapshot` calls `handle_snap_mgr_gc`. That method lists idle snapshots, groups consecutive snapshot keys by `region_id`, and sends each group to the owning peer as a casual GC message. If the peer router is disconnected because the system is shutting down, it treats that as success. If a region mailbox is disconnected but the store is not shutting down, it loads each snapshot for GC and deletes it directly because the peer is considered destroyed. Full mailboxes are tolerated and the snapshots will be retried later. After GC handling, the runner sends `StoreMsg::GcSnapshotFinish` through the store router.

`DeleteSnapshotFiles` loads snapshot metadata if necessary, logs but continues on metadata-load failure, and then deletes the snapshot with the provided `check_entry` flag. Failures are logged.

## State and Persistence Behavior
The worker changes snapshot filesystem state through `SnapManager`. `GcSnapshot` itself schedules peer-side cleanup and only deletes directly on disconnected-region fallback. `DeleteSnapshotFiles` performs immediate deletion. No raft log or KV engine state is modified, but snapshot files are persistent artifacts, and `check_entry` controls whether deletion validates entry metadata.

## Dependencies and Integration Points
It depends on `KvEngine`, `RaftEngine`, crossbeam `TrySendError`, failpoints, `SnapKey`, `Snapshot`, `SnapManager`, `RaftRouter`, `StoreRouter`, `PeerMsg`, `CasualMessage`, and `StoreMsg`. It integrates with peer FSM casual messages and store-level GC completion bookkeeping.

## Risks and Edge Cases
The grouping assumes `list_idle_snap` returns keys in a useful region grouping order; otherwise duplicate region sends still work but are less efficient. Full mailboxes silently defer work. Direct deletion on disconnected peers depends on correctly distinguishing store shutdown from destroyed peer mailboxes. Metadata load failures are logged but do not stop deletion attempts.

## Test Signals
There are no direct unit tests in this file. Behavior is instrumented with failpoint `peer_2_handle_snap_mgr_gc` and is typically covered by snapshot manager, peer destruction, and raftstore snapshot GC integration tests.
