# sources/storage-engines/tikv/tests/failpoints/cases/test_snap.rs

## Purpose
This suite validates raft snapshot generation, sending, receiving, application, retry, GC, recovery, and shutdown behavior. It targets failure windows where snapshots overlap split ranges, network/resolve errors interrupt transfer, peers are destroyed during pending snapshot application, raft writes fail after KV snapshot writes, and receiver concurrency limits serialize ingestion.

## Important APIs, Types, And Functions
Helpers `must_empty_dir` and `assert_snapshot` poll snapshot directories. The tests use `configure_for_snapshot`, `configure_for_request_snapshot`, `new_node_cluster`, `new_server_cluster`, `test_raftstore_v2` variants, `MessageTypeNotifier`, `RegionPacketFilter`, `DropSnapshotFilter`, `IsolationFilterFactory`, `get_snap_mgr`, raft-engine debug APIs, and snapshot manager stats. Key failpoints include `region_gen_snap`, `transport_on_send_snapshot`, `snapshot_delete_after_send`, `snapshot_enter_do_build`, `apply_pending_snapshot`, `destroy_peer_after_pending_move`, `skip_schedule_applying_snapshot`, `peer_2_handle_snap_mgr_gc`, `before_no_ready_gen_snap_task`, `before_region_gen_snap`, `get_snapshot_for_gc`, `receiving_snapshot_net_error`, `worker_gc_raft_log`, `raft_before_save_on_store_1`, `APPLY_COMMITTED_ENTRIES`, `RESET_APPLY_INDEX_WHEN_RESTART`, `snap_send_duration_timeout`, `snap_send_timer_delay`, `snap_send_error`, `receiving_snapshot_callback`, `snap_gen_precheck_failed`, and `post_recv_snap_complete*`.

## Control Flow
Early tests verify snapshot file lifecycle: overlapped snapshots from pre-split ranges are cleaned, snapshot sending retries after address resolution failure, in-flight generation tasks are canceled or replaced when deleted after send, and snapshot directories empty after send completion. Pending-snapshot destruction tests isolate a peer, force it into applying state, remove and recreate peers, pause destroy/apply paths, restart nodes, and assert the correct peer eventually applies data and snapshot files are GCed.

Several tests inject old or failed snapshots. `test_receive_old_snapshot` captures an old snapshot, lets the peer catch up with newer data, replays the old snapshot, then removes/re-adds peers across a split to ensure pending snapshot metadata is not left behind. Recovery tests corrupt ordering between KV snapshot application and raftdb state persistence, stop/restart nodes, and assert the snapshot is re-applied cleanly and stale raft logs are removed. Other cases validate snapshot generation from no-new-commit ready, cancellation when log GC advances the truncated index, cleanup after GC failures, send timeouts, corrupted SST retry, and send-error cleanup.

The receiver-busy tests configure `concurrent_recv_snap_limit = 1` and orchestrate two regions sending snapshots to the same store. They assert snapshot generation pauses or precheck fails while the receiver is busy, then both regions complete when the first receive finishes.

## State And Persistence Behavior
Persistent artifacts include `.meta` and SST snapshot files, raft logs, `RaftLocalState`, region local state, and KV data in RocksDB. Transient state includes snapshot manager sending/receiving counters, pending snapshot regions, peer `Applying` state, raft progress in `Snapshot`, and receiver precheck reservations. The tests emphasize cleanup: stale snapshot files, stale raft logs before first index, pending metadata, and leader-side generated snapshots must not survive after failure recovery.

## Dependencies And Integration Points
These tests connect raftstore peer FSMs, apply FSMs, snapshot manager, server transport, raft engine, RocksDB snapshot ingestion, PD membership changes, failpoint scheduling, and both raftstore v1/v2 clusters through `test_case`.

## Risks And Edge Cases
Risks include peers stuck in snapshot progress after send failure, panics when destroying peers with pending apply tasks, old snapshots resurrecting stale metadata, snapshot generation using a truncated index, leaked receiving counters, incomplete raftdb recovery, corrupted snapshot retry failure, send-timeout leaks, and busy receivers allowing duplicate or unbounded snapshot generation.

## Test Signals
Signals are engine value presence/absence, snapshot directory emptiness or expected files, snapshot manager counters, raft log emptiness after recovery, peer state transitions, received snapshot notifications, PD peer membership checks, no panic during shutdown, and successful writes after snapshot recovery.
