# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/merge/mod.rs

## Purpose
Defines shared merge module exports, source checkpoint path naming, and the source-region `MergeContext` state wrapper used by prepare, commit, rollback, and proposal control.

## Important APIs, Types, And Functions
The module exposes `commit`, `prepare`, and `rollback`. `MERGE_SOURCE_PREFIX` names source checkpoint tablets. `merge_source_path` derives the on-disk checkpoint path from a `TabletRegistry`, source region id, and prepare-merge commit index. `MergeContext` stores an optional `PrepareStatus` and provides `from_region_state`, `maybe_take_pending_prepare`, `max_compact_log_index`, and `prepare_merge_index`. Peer helpers include `update_merge_progress_on_became_follower`, `calculate_min_progress`, and `applied_merge_state`.

## Control Flow
When a peer is constructed from `RegionLocalState::Merging`, `from_region_state` recreates merge context as `PrepareStatus::Applied`, allowing restarted source peers to resume commit checks. Pending prepare proposals held behind a pessimistic-lock fence are released by `maybe_take_pending_prepare` once apply reaches the fence. Leaders use `calculate_min_progress` before prepare or commit scheduling to find the minimum matched and committed raft indexes across peers and to reject merge if any peer is snapshotting.

## State And Persistence Behavior
This file does not persist data directly, but it interprets persisted `RegionLocalState` and `MergeState` and maps them to in-memory `MergeContext`. The source checkpoint path is part of the persistent tablet layout and is later destroyed by commit or rollback cleanup. `prepare_merge_index` reflects the persisted merge state's commit index.

## Dependencies And Integration Points
Used by `prepare.rs` for fencing and source checkpoint creation, `commit.rs` for finding applied merge state and checkpoint paths, `rollback.rs` for cleanup, `control.rs` for merge proposal gating, and compact-log logic through `max_compact_log_index`.

## Risks And Edge Cases
`calculate_min_progress` rejects pending snapshots because merging a source peer with an invalid target snapshot state would be unsafe. It compensates for inaccurate raft progress when min matched is below min committed by raising matched to committed. Follower transitions clear transient trim/fence checks to avoid stale leader-only merge progress.

## Test Signals
There are no local tests. Signals are indirect through prepare/commit/rollback behavior, restart recovery from `PeerState::Merging`, assertions around merge status transitions, and logs warning when raft progress is inconsistent.
