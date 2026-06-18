# sources/storage-engines/tikv/tests/failpoints/cases/test_stale_read.rs

## Purpose
This file validates node-level stale-read prevention for local lease reads and ReadIndex during split, merge, leader transfer, and peer destruction. It ensures old-region leaders cannot return stale values once another region or leader owns the key range, and that queued reads fail with explicit errors rather than timing out or returning obsolete data.

## Important APIs, Types, And Functions
`stale_read_during_splitting` drives both left-derive and right-derive split modes. `must_not_stale_read` writes a newer value through the new region, compares old/new leader local reads and ReadIndex reads, pauses `before_propose_readindex`, then releases the split/merge failpoint and expects an error. `must_not_eq_on_key` performs the read comparison. Other tests use `configure_for_lease_read`, `configure_for_merge`, `configure_for_request_snapshot`, PD split/merge, `Callback`, `read_on_peer`, `make_cb_rocks`, and raftstore message filters.

## Control Flow
Split tests pause apply on the old leader's store after initiating split, wait for another store to lead the new split region, write through the new region, and verify both local read and ReadIndex against the old region return errors, not stale values. The merge test creates two regions with different leaders, triggers merge, pauses commit-merge on all but one peer, manually adjusts source epoch to the prepare-merge epoch, and applies the same stale-read denial pattern to a key now covered by the target region.

`test_read_index_when_transfer_leader_2` delays raft messages to the old leader, queues read-index requests before and after leader transfer, then delivers heartbeat/append messages in one batch so role change and read completion race; both queued reads must return `stale_command`. `test_read_after_peer_destroyed` pauses destroy, queues a read on the removed peer, resumes destroy, waits for async raft-GC progress, and expects `region_not_found`. `test_stale_read_during_merging_2` pauses at `leader_commit_prepare_merge` after prepare-merge commit and confirms the leader lease is suspected early enough that local reads time out rather than returning an obsolete value.

## State And Persistence Behavior
The tested state is region epoch/range ownership, leader leases, pending read queues, ReadIndex proposals, peer destroy state, and merge prepare/commit progress. Persistent KV values establish the stale-versus-current answers, while transient raftstore state decides whether reads are served locally, queued, rejected, or timed out.

## Dependencies And Integration Points
The file integrates raftstore local read, ReadIndex, PD split/merge scheduling, leader transfer, message filtering, async command callbacks, destroy-peer flow, and failpoints in split/merge/read-index paths.

## Risks And Edge Cases
Risks include old leaders serving stale local reads during slow split, ReadIndex requests queued before role change succeeding after leadership is lost, prepare-merge not suspecting leader lease early enough, removed peers answering reads before destroy completes, and split derive mode differences hiding a stale key under old and new ranges.

## Test Signals
Signals include the new region returning the latest value, old region reads carrying header errors, queued reads returning `stale_command`, destroyed-peer reads returning `region_not_found`, expected timeout while merge leader is paused, and no stale value equality from the old owner.
