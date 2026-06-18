# sources/storage-engines/tikv/tests/failpoints/cases/test_merge.rs

## Purpose
This is the central failpoint regression suite for raftstore region merge. It validates prepare/commit/rollback merge correctness across raftstore v1 and v2, restarts, snapshots, log compaction, leader transfer, pessimistic locks, timestamp synchronization, source-peer destruction, read delegates, and atomic snapshot races.

## Important APIs, Types, and Functions
- Tests use `configure_for_merge`, `must_split`, `must_try_merge`, `pd_client.must_merge`, `merge_region`, `check_merged_timeout`, `region_local_state`, `truncated_state`, `raft_local_state`, and direct raft command construction.
- Important state types include `RegionLocalState`, `PeerState`, `RaftMessage`, `PessimisticLock`, `LastChange`, `LocksStatus`, `ReadDelegate`, and raftstore/v2 `PeerMsg` and `PeerTick`.
- Custom filters `MsgTimeoutFilter` and `MsgVoteFilter` intercept leader-transfer and election traffic.
- Failpoints cover scheduling, applying, persistence, compact log, snapshot handling, lock proposal, disk-full, destroy-peer, and commit/rollback race boundaries.

## Control Flow
The file progresses from basic rollback and restart scenarios to increasingly specific historical regressions. Early tests verify rollback after target epoch changes and restart recovery from `Merging` state. Catch-up-log tests isolate peers, compact raft logs, and ensure lagging peers either recover by logs or snapshot. Snapshot tests deliver pre-merge and post-merge snapshots together or apart. Later tests stress compact-log interactions after prepare merge, failed-then-successful merges to the same target, leader transfer during commit, cascading merge with apply yield, majority rollback rules, and protection against writes to source after merge. The final group covers snapshot atomicity, timestamp max-ts synchronization, source read delegate lifecycle, pessimistic-lock proposal ordering, source peer destruction while merging, deterministic commit-vs-rollback behavior, lost merging state on restart, atomic snapshot destroy races, raft-log GC after merge, and apply-ahead-of-persist recovery.

## State and Persistence Behavior
The suite inspects persisted raft CF region state to distinguish `Normal`, `Merging`, `Tombstone`, and `Applying`. It verifies epoch version/conf-ver changes after split, prepare merge, rollback, conf change, and commit merge. Several tests stop nodes with unpersisted raft logs or applied-but-not-persisted indexes to ensure recovery does not lose merge state or compact required entries. Snapshot tests ensure source-peer destruction and target snapshot application are atomic enough to survive crash and restart. Pessimistic-lock tests validate `LocksStatus` transitions and that in-memory locks are proposed or rejected at correct merge stages. Timestamp tests protect raw/txn writes until max timestamp is synced after merge.

## Dependencies and Integration Points
The file integrates PD operators, raftstore peer FSMs, apply FSMs, raft log engine reads, Rocks CF reads, gRPC KV client prewrite/lock RPCs, concurrency manager locks, raftstore v2 router ticks, packet filters, and storage snapshots. It is a heavy cross-layer suite touching scheduling, persistence, transaction lock memory, leader transfer, and region metadata.

## Risks and Test Signals
Risks include data loss from rollback after commit, stale merge state after restart, compacted logs needed by commit merge, panic from missing source peers, accepting stale writes to source regions, incorrect pessimistic lock status, non-deterministic commit/rollback, and read delegate removal too early. Test signals include persisted `PeerState`, PD merged checks, successful puts after recovery, absence/presence of keys on isolated stores, lock status assertions, response error checks, and failpoint callbacks at exact state-machine boundaries.
