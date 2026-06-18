# sources/storage-engines/tikv/components/raftstore-v2/src/operation/misc.rs

## Purpose
Handles miscellaneous store-level maintenance, currently snapshot garbage collection for tablet snapshots.

## Important APIs, Types, And Functions
`StoreFsmDelegate::on_snapshot_gc` is the tick handler. `Store::on_snapshot_gc` lists snapshot paths from `snap_mgr`, parses them into `TabletSnapKey`, groups keys by region id, and routes `PeerMsg::SnapGc` to the owning peer.

## Control Flow
The store FSM tick calls the store helper, logs any cleanup-listing error, and reschedules `StoreTick::SnapGc` using `snap_mgr_gc_tick_interval`. For each region group, the store router attempts to send the cleanup message. If the peer mailbox is disconnected and the store is not shutting down, the keys are scheduled directly to the tablet worker as `tablet::Task::SnapGc`.

## State And Persistence Behavior
The file does not mutate raft metadata directly. Snapshot files are external filesystem artifacts owned by the snapshot manager or tablet worker. Persistence behavior is cleanup-oriented: stale snapshot files are discovered and later deleted by peer or tablet-worker handling.

## Dependencies And Integration Points
Depends on `TabletSnapKey::from_path`, `snap_mgr.list_snapshot`, the peer router, `PeerMsg::SnapGc`, and the tablet worker scheduler. It integrates with peer snapshot lifecycle and store tick scheduling.

## Risks And Edge Cases
Malformed snapshot paths propagate as errors from `TabletSnapKey::from_path`. Router disconnection is ambiguous between a removed peer and shutdown; shutdown suppresses fallback work, while non-shutdown routes cleanup to the tablet worker. Grouping by region is important to avoid sending unrelated snapshot keys to one peer.

## Test Signals
There are no direct tests in this file. Signals are snapshot manager directory contents after GC ticks, warnings for cleanup failures, and tablet worker `SnapGc` task scheduling when a peer is absent.
