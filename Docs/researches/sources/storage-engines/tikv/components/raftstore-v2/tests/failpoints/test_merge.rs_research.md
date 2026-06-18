# sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_merge.rs

## Purpose
This file stress-tests raftstore-v2 merge recovery and conflict handling under failpoint-controlled crash/race windows. It covers source/target replay after restart, early source destruction, rollback when target ranges change, and conflicts with concurrent or already-finished target merges.

## Important APIs, Types, and Functions
- `test_source_and_target_both_replay()` injects `after_acquire_source_checkpoint` to abort after checkpoint acquisition, restarts, and waits for source data to appear in target.
- `test_source_destroy_before_target_apply()` combines `force_send_catch_up_logs` and `after_acquire_source_checkpoint` so the source is destroyed before target apply, then validates replay after restart.
- `test_rollback()` triggers a split from inside `start_commit_merge` and expects the source region to roll back and remain writable.
- `test_merge_conflict_0()` pauses `apply_commit_merge` for target merge 2+3, starts merge 1+2, and waits for `apply_rollback_merge`.
- `test_merge_conflict_1()` blocks ask-target for merge 1+2, merges 2+3 first, then forces check-merge and expects rollback.

## Control Flow
All tests use split helpers to create adjacent regions, write range-marker keys, then call `merge_region()` with specific failpoints active. Recovery tests restart the cluster and poll stale snapshots. Conflict tests coordinate with failpoint callbacks and channels, then attempt writes to the original source region until success proves rollback completed. The first conflict test also waits for the third region to apply current term to avoid nested future-pool leakage noted in comments.

## State and Persistence Behavior
The tests validate merge checkpoints, source destruction markers, target apply state, region epoch/range state, and data replay into the merged target. They intentionally cross restart boundaries to prove checkpoint/replay data is durable enough even when source and target have partial progress.

## Dependencies and Integration Points
They depend on cluster split/merge/life helpers, router stale snapshots, `PeerTick::CheckMerge`, failpoint callbacks, raftstore-v2 merge apply code, and tablet checkpoint handling.

## Risks and Edge Cases
- Source checkpoint acquisition followed by crash must be replayable by both source and target.
- Source destruction before target apply must not orphan data or prevent target replay.
- Merge commit must detect target range changes and roll back rather than corrupt overlapping regions.
- Concurrent merge conflicts can otherwise leave regions unwritable or merged into destroyed targets.

## Test Signals
Signals include source key visible in target after restart, old source peer nonexistence, rollback failpoint callback receipt, and successful writes to non-merged source regions after conflict resolution.
