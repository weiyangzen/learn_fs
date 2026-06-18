# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/merge/rollback.rs

## Purpose
Implements rollback for a prepared but uncommitted merge, returning the source region from `PeerState::Merging` to `Normal` and cleaning merge-mode in-memory state.

## Important APIs, Types, And Functions
`RollbackMergeResult` carries the prepare commit index and updated `RegionLocalState`. `Peer::on_reject_commit_merge` converts a target-side rejection into a local `RollbackMerge` admin proposal if the prepare index matches. `Apply::apply_rollback_merge` updates region state. `Peer::on_apply_res_rollback_merge` persists and installs the result. `Peer::rollback_merge` performs local cleanup and can also be called when a snapshot rolls back merge without a proposal.

## Control Flow
If a target peer rejects commit merge due to stale epoch, the source peer checks that its applied prepare index equals the rejection index, builds a rollback admin request, and passes it through normal admin proposal handling. Apply verifies the local state is `Merging` and the requested commit equals the persisted merge state, bumps region version to avoid duplicate rollback ambiguity, clears merge state, and returns a result. Peer result handling updates store metadata/readers, writes the new local state to the state-change batch, updates storage, and calls `rollback_merge` to leave merge mode.

## State And Persistence Behavior
Rollback persists the source region as `PeerState::Normal` with merge state removed and region version incremented. Cleanup records the source checkpoint path as a tombstone tablet path rather than deleting immediately, leaves `ProposalControl` prepare-merge mode, drops `MergeContext`, resumes read progress, and restores pessimistic lock status to normal on leaders.

## Dependencies And Integration Points
Uses `merge_source_path`, admin request construction, `ProposalContext::ROLLBACK_MERGE` via admin dispatch, `RegionChangeReason::RollbackMerge`, state-change persistence, read progress, lock status, PD heartbeat, and target rejection messages from `commit.rs`.

## Risks And Edge Cases
Index mismatches are ignored before proposing but panic during apply/result handling if persisted state does not match the rollback request. Cleanup assumes an applied prepare merge exists. The checkpoint is deliberately retained for tombstone cleanup so restarts can avoid rebuilding or leaking it.

## Test Signals
There are no local tests. Signals are rollback admin metrics, logs for ignored stale rejections, panics for inconsistent merge state, state-change writes, read-progress resume, lock status normalization, and PD heartbeat after leader rollback.
