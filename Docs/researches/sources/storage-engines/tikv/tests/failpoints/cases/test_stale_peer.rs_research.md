# sources/storage-engines/tikv/tests/failpoints/cases/test_stale_peer.rs

## Purpose
This failpoint suite validates stale-peer detection, cleanup, destruction, restart recovery, and raft-log cleanup. It covers peers removed from PD membership, peers stuck applying snapshots, stale learners, uninitialized peers, delayed async destroy, and local-reader updates after removal.

## Important APIs, Types, And Functions
The tests use `new_node_cluster`/`new_server_cluster`, `configure_for_snapshot`, PD peer operations, `must_gc_peer`, `must_region_cleared`, raft-engine debug APIs, `RaftLocalState`, `PeerState`, `RaftMessage`, and `block_on(pd_client.get_region_by_id)`. They run selected cases against raftstore v1 and v2 using `test_case`. Failpoints include `peer_check_stale_state`, `manually_set_store_offline`, `raftstore_set_region_after_change_peer`, `apply_on_add_node_1_2`, `on_handle_apply_1003`, `region_apply_snap`, `worker_gc_raft_log`, and `destroy_peer_after_pending_move`.

## Control Flow
`test_one_node_leader_missing` configures a single-node cluster with carefully ordered stale-state intervals and asserts stale-state checking should not run in a valid single-node leadership case. `test_clean_stale_peer` marks a store offline, removes a peer, and verifies offlined stores retain data files; after the store returns to serving, adding a new peer resyncs data and removing it later clears data. `test_node_update_localreader_after_removed` pauses an apply path, isolates and removes a peer, waits for stale GC, then resumes apply and asserts the removed peer does not reinsert stale local-reader state.

Restart and snapshot tests cover learners and applying peers. A stale learner paused in apply must catch up after restart. A peer applying a snapshot can be removed via tombstone message; once snapshot apply resumes, it should destroy itself without needing another message trigger. Uninitialized peer tests ensure destroying a new learner does not let an older isolated peer on the same store revive after partitions change.

The log cleanup tests simulate lost raft-log GC tasks, ensure stale logs exist below first index, then destroy or snapshot-recover the peer and assert old logs are deleted. `test_async_destroy_peer_delayed` pauses peer destroy, adds a replacement peer on the same store, resumes destroy, removes the replacement, and confirms the region data is cleared.

## State And Persistence Behavior
State under test includes raft local state, hard-state commit/last-index, peer local state (`Applying`, cleared/tombstone), local-reader delegates, engine data files, region data in all CFs, pending destroy tasks, and stale raft logs. Persistent cleanup must distinguish offlined stores, removed serving peers, uninitialized peers, and replacement peers sharing a store.

## Dependencies And Integration Points
The suite integrates PD membership, raftstore stale-state checking, snapshot apply cancellation, async destroy, SnapManager offlined state, local reader delegate updates, raft log GC worker, raft engine read/debug APIs, and simulator message filters.

## Risks And Edge Cases
Risks include unnecessary stale-state panic in a one-node cluster, deleting data for an offlined store too early, stale apply callbacks updating local readers after removal, learners losing committed-but-unapplied logs across restart, snapshot-apply peers surviving tombstone removal, old isolated peers reviving after a newer uninitialized peer is destroyed, stale raft logs left after destroy, and delayed destroy deleting data for a replacement peer incorrectly.

## Test Signals
Signals include engine file presence, value presence/absence after peer removal/addition, `must_region_not_exist`, `must_region_cleared`, local state reaching `Applying`, raft entries becoming empty, callbacks firing at failpoints, and successful reads after restart catch-up.
