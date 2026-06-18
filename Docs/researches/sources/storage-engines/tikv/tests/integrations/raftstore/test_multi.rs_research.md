<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_multi.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_multi.rs

## Purpose
This file tests multi-node raftstore behavior under normal writes, deletes, leader crashes, restarts, lost majorities, message delay/drop, uncommitted logs, stale proposals, consistency checks, batch writes, catch-up, and pessimistic-lock cleanup on leader loss.

## Important APIs, Types, and Functions
Shared helpers include `test_multi_base`, `test_multi_base_after_bootstrap`, `test_multi_leader_crash`, `test_multi_cluster_restart`, `test_multi_lost_majority`, `test_multi_random_restart`, `test_leader_change_with_uncommitted_log`, `test_read_leader_with_unapplied_log`, `get_with_timeout`, `test_remove_leader_with_uncommitted_log`, `test_consistency_check`, and `test_batch_write`.

It uses `new_node_cluster`, `new_server_cluster`, `must_put`, `must_get`, `must_delete`, `assert_quorum`, `RegionPacketFilter`, `DelayFilter`, `RandomLatencyFilter`, `DropPacketFilter`, `RaftStoreRouter`, callbacks, `MessageType`, `PessimisticLock`, and snapshot transaction extensions.

## Control Flow and Behavior
The baseline tests write/delete keys and assert quorum replication. Network tests wrap the same flow with fixed latency, random latency, or packet loss. Failure tests stop leaders or random nodes, verify new leader election and catch-up, restart whole clusters, and verify no leader exists after majority loss.

The uncommitted-log tests create followers with appended but unapplied entries, transfer leadership, and ensure the new leader does not serve stale reads or lose committed entries. Proposal cleanup tests make raft drop proposals during transfer-leader edge cases and require callbacks to be completed with errors. Batch write tests check atomicity when a batch crosses region ranges.

## State and Persistence
The tests assert data in each engine, raft leadership state, applied/unapplied log effects, callback cleanup, region-not-found behavior after removing the leader, and transaction extension memory state. Cluster restart tests verify data survives shutdown/start; catch-up tests verify a stopped peer receives missed logs after restart.

## Dependencies and Integration Points
The file integrates raftstore routing, simulated transports, PD membership updates, storage snapshots, local engine reads, raft callbacks, and pessimistic transaction lock memory. It covers both node and server cluster variants where applicable.

## Risks
Timing-sensitive leader election and packet filtering can make tests fragile. Key risks are stale reads from a new leader with unapplied logs, callbacks leaked after dropped proposals, writes accepted by a removed leader, batch partial application, and pessimistic locks surviving on a peer that lost leadership.

## Test Signals
Signals include exact key equality/nonexistence on individual engines, quorum predicates, leader identity changes, callback receipt within timeout, stale-command and region-not-found errors where expected, consistency-check survival, and empty pessimistic-lock memory after leadership returns.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_multi.rs -->
