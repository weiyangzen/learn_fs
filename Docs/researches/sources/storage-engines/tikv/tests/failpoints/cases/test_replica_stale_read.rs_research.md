# sources/storage-engines/tikv/tests/failpoints/cases/test_replica_stale_read.rs

## Purpose
This failpoint suite validates TiKV replica stale-read correctness when follower/learner replicas answer reads from local state using resolved-ts and replica read-state metadata. It stresses the conditions under which a replica can serve an old timestamp without issuing ReadIndex, and when it must reject with `data_is_not_ready` or fall back to normal leader snapshot reads.

## Important APIs, Types, And Functions
`prepare_for_stale_read` and `prepare_for_stale_read_before_run` build a three-node `ServerCluster`, enable `resolved_ts`, transfer leadership, construct a `PeerClient`, and install `propose_readindex_from_follower=panic` to prove follower stale reads do not go through ReadIndex. Test code uses `PeerClient` helpers such as `must_kv_write`, `must_kv_read_equal`, `must_kv_prewrite`, `must_kv_commit`, `must_kv_prewrite_one_pc`, `must_kv_prewrite_async_commit`, `must_kv_pessimistic_lock`, and low-level `kv_read`. PD and raftstore control is via `TestPdClient`, `must_split`, `must_merge`, `must_transfer_leader`, `RegionPacketFilter`, `IsolationFilterFactory`, and failpoints including `before_sync_replica_read_state`, `on_apply_res`, `raft_before_applying_snap_finished`, `apply_before_prepare_merge_2_3`, and `on_schedule_merge`.

## Control Flow
The basic replication tests write data on the leader, block `MsgAppend` to a follower, and assert that reads at timestamps already applied succeed while reads at newer commit timestamps are rejected. The lock tests leave unresolved MVCC locks and verify safe-ts is bounded by the minimum lock start timestamp, then advances after locks commit. Apply-index tests arrange ordering races where resolved-ts, apply-index, and synchronized `(apply_index, safe_ts)` tuples are updated in different orders, proving followers cannot be advertised a safe timestamp for data they have not applied.

Snapshot and merge tests move the same stale-read invariant across region lifecycle events. While a follower is applying a snapshot, stale reads should return `data_is_not_ready` with safe-ts zero, then resume after the snapshot is applied. Merge tests assert that target-region safe-ts becomes the minimum of source and target state, source leaders stop advancing safe-ts during merge, rollback resumes advancement, and reading a source range after target merge does not expose writes hidden behind a source lock.

## State And Persistence Behavior
The observable state is MVCC data and locks, per-peer apply index, resolved-ts/safe-ts, replica read-state broadcast state, region epoch and peer topology, snapshot application state, and concurrency-manager max-ts. Tests deliberately persist data through raft replication, snapshots, merges, and peer replacement. `test_stale_read_future_ts_not_update_max_ts` confirms a future-timestamp stale read does not raise the leader concurrency manager's max-ts, preserving later async-commit and 1PC transactions with smaller timestamps.

## Dependencies And Integration Points
The file integrates TiKV storage RPC behavior through `PeerClient`, PD region scheduling through `TestPdClient`, raftstore message filtering, failpoint injection, resolved-ts advancement, snapshot apply, merge scheduling, and learner peer creation. It is a cross-layer test for MVCC, concurrency manager, raftstore replica state, and PD-driven region membership.

## Risks And Edge Cases
The main risks are serving stale or future data when a follower has safe-ts but lacks the corresponding apply index, failing to reset safe-ts during snapshot apply, incorrectly merging lock resolver state, updating source safe-ts after merge, treating pessimistic locks from old leaders as blockers, serving stale reads from learners before they are ready, or allowing stale reads to perturb max-ts.

## Test Signals
Success is signaled by exact value reads at allowed timestamps, `data_is_not_ready` region errors at unsafe timestamps, safe-ts zero while snapshot apply is paused, absence of follower ReadIndex proposals, successful post-snapshot/post-merge reads, and successful async-commit/1PC writes after future-timestamp stale reads.
