# sources/storage-engines/tikv/src/server/snap.rs

## Purpose
`snap.rs` implements TiKV's v1 snapshot transport worker. It sends raft snapshots to remote TiKV nodes over gRPC, receives incoming snapshot chunk streams, writes snapshot files through `SnapManager`, feeds completed snapshot raft messages back into raftstore, enforces snapshot send/receive concurrency limits, refreshes snapshot I/O limits from dynamic config, and delegates tablet-snapshot receive traffic for raftstore v2/TiFlash cases.

## Important APIs, Types, and Functions
`Task` is the worker input enum: `Recv` for v1 snapshot client-streaming RPCs, `RecvTablet` for raftstore-v2 tablet snapshot duplex streams, `Send` for outbound snapshots, `RefreshConfigEvent`, and `Validate`. `Runner<R: RaftExtension>` implements `Runnable<Task>` and owns the gRPC environment, `SnapManager`, Tokio runtime, raft router, security manager, config tracker/current config, and atomic send/receive counters.

`send_snap` builds an outbound gRPC snapshot future. It decodes `RaftSnapshotData` from the raft message, derives a `SnapKey`, registers `SnapEntry::Sending`, opens the snapshot file, streams a first chunk containing the raft message followed by file chunks, waits for the remote `Done`, records stats, deregisters, and deletes the local sending snapshot.

`SnapChunk` is a `Stream` over `(SnapshotChunk, WriteFlags)`. It emits the first metadata chunk, then reads the snapshot file in `SNAP_CHUNK_LEN` one-megabyte chunks under the correct `IoType`.

`RecvSnapContext` parses the first inbound chunk, verifies it contains a raft message, derives the snapshot key and I/O type, opens a receiving snapshot file unless it already exists, and later `finish`es by saving the file and feeding the raft message to `RaftExtension`.

`recv_snap` consumes the inbound stream. It creates a receive context, registers `SnapEntry::Receiving`, writes every non-empty data chunk, saves the file, feeds raftstore, and replies with `Done` or a gRPC failure. `cleanup_after_recv` releases the receive counter and notifies `SnapManager::recv_snap_complete`.

Config and limit helpers include `get_snap_timeout`, `Runner::refresh_cfg`, and `Runner::receiving_busy`. `DEFAULT_POOL_SIZE`, `SNAP_SEND_TIMEOUT_DURATION`, `MIN_SNAP_SEND_SPEED`, and `SNAP_CHUNK_LEN` define runtime defaults.

## Control Flow
Outbound snapshot flow starts when raftstore schedules `Task::Send`. The runner rejects the task if `sending_count` has reached `concurrent_send_snap_limit`; otherwise it increments the counter, calls `send_snap`, spawns the returned future on the snapshot runtime, and invokes the supplied callback with success or failure. `send_snap` sends the raft snapshot message before data bytes so the receiver can derive metadata and open the correct file. It races send/receive completion against a timeout computed as the larger of the default timeout and `size / MIN_SNAP_SEND_SPEED`.

Inbound v1 flow starts when `kv.rs` schedules `Task::Recv` from the gRPC `snapshot` service method. The runner checks `receiving_busy`, increments `recving_count`, and spawns `recv_snap`. `recv_snap` reads the head chunk, initializes `RecvSnapContext`, records the region id for cleanup, writes remaining chunks into the receiving snapshot file, and finally calls `finish` to save and feed the raft message. The sink returns `Done` only after the snapshot has been saved and delivered to raftstore.

Inbound tablet flow is similar at the runner level but delegates the stream to `crate::server::tablet_snap::recv_snap` with a tablet snapshot manager, raft router, limiter, and the v1 `SnapManager` for shared receive-complete coordination. If tablet snapshots are unsupported, it fails the stream with `UNIMPLEMENTED`.

Dynamic config refresh arrives as `Task::RefreshConfigEvent`. The runner pulls from `VersionTrack<Config>`, updates snapshot speed limit, max total snapshot size, minimum ingest CF size, concurrent receive limit, and its local config copy. `Task::Validate` gives tests or callers a read-only view of the current config.

## State and Persistence Behavior
Snapshot file state is mediated by `SnapManager`. Sending registers `SnapEntry::Sending` and deregisters through `DeferContext`; receiving registers `SnapEntry::Receiving` and deregisters with `defer!`. The send path deletes the local sending snapshot after the remote side responds or the send fails. The receive path writes chunk bytes into a snapshot file, calls `Snapshot::save`, and only then feeds the raft message with the `is_snapshot` flag set.

`recving_count` and `sending_count` are process-local concurrency guards. `cleanup_after_recv` decrements receive count and calls `recv_snap_complete(region_id)` so the snapshot manager's limiter releases region-level resources. Snapshot statistics are collected after successful sends when total duration is at least one second, including transport size, generate duration, send duration, and total duration.

I/O classification is preserved from snapshot metadata: balance snapshots use `IoType::LoadBalance`, other snapshots use `IoType::Replication`. `WithIoType` wraps file reads, writes, saves, and receives so lower layers can account or throttle by I/O class.

## Dependencies and Integration Points
The module depends on `grpcio` client/server streaming primitives, `kvproto` raft snapshot messages and PD snapshot stats, `SnapManager`/`SnapKey`/`Snapshot`, `SecurityManager` for secure outbound channels, `tikv_kv::RaftExtension` for delivering completed snapshots, TiKV config tracking, global timer, metrics, failpoints, Tokio runtime construction, and tablet snapshot support. `kv.rs` schedules receive tasks, while raftstore schedules send tasks with callbacks.

Outbound connections use the server `Config` gRPC settings for stream window size, keepalive, compression algorithm/level, and minimum compression size. Security setup is centralized through `security_mgr.connect`.

## Risks and Edge Cases
The first chunk is mandatory and must contain the raft message; empty streams or data-only first chunks fail. Empty data chunks after the head are treated as errors. If the receiving snapshot file already exists, the receiver skips byte reception and immediately feeds the raft message, relying on `SnapManager` file presence as idempotence.

Timeout behavior scales with snapshot size, but very slow networks below `MIN_SNAP_SEND_SPEED` can still fail. Send completion deletes the snapshot file even after errors, so callers must be prepared to regenerate failed snapshots. Counter cleanup is manual; v1 receive uses `cleanup_after_recv`, while tablet receive decrements directly after the delegated future. Any future refactor must preserve decrement and `recv_snap_complete` ordering.

Concurrency checks happen before incrementing counters and are process-local. Config refresh changes limits asynchronously, so an already-running workload may temporarily exceed a newly lowered limit. `Task::Send` clones `self.cfg` before calling `send_snap`, so an in-flight send uses the config snapshot from scheduling time.

## Test Signals
This file contains no local unit tests, but it is instrumented with failpoints for send errors, send timer delay, send timeout duration, delete-after-send, send task scheduling, receive callbacks, and receive network errors. Useful coverage should exercise missing snapshot files, timeout selection by size, first-chunk validation, existing-file receive idempotence, receive cleanup on success and failure, send/receive concurrency limits, config refresh effects on `SnapManager`, and tablet-snapshot unsupported behavior.
