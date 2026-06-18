# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/merge/prepare.rs

## Purpose
Implements `PrepareMerge`, the source-region phase that validates merge eligibility, fences in-memory pessimistic locks, persists `PeerState::Merging`, and creates the source checkpoint consumed by commit merge.

## Important APIs, Types, And Functions
`PreProposeContext` carries `min_matched` and remaining raft-entry size budget for transferred locks. `PrepareStatus` is the source merge FSM: `WaitForTrimStatus`, `WaitForFence`, `CatchUpLogs`, and `Applied`. `PrepareMergeResult` returns new region state and `MergeState`. Main peer methods are `propose_prepare_merge`, `validate_prepare_merge_command`, `check_logs_before_prepare_merge`, `start_check_trim_status`, `merge_on_availability_response`, `check_pessimistic_locks`, `retry_pending_prepare_merge`, `propose_locks_before_prepare_merge`, and `post_prepare_merge_fail`. Apply-side `apply_prepare_merge` mutates region state and checkpoints the tablet.

## Control Flow
Proposal first validates that source and target are sibling regions on the same stores and not in joint consensus. It then runs three ordered gates: availability/trim checks against source and target peers, raft-log gap and forbidden-admin scanning, and pessimistic-lock fencing. Trim checks send `MsgAvailabilityRequest` to all relevant peers and resume through a pre-flush callback with `PRE_FLUSH_FINISHED`. If locks exist and apply has not caught up to the last log, `WaitForFence` rejects new writes until apply reaches the fence, then the original request is retried. Locks are serialized as lock-CF puts before the actual `PrepareMerge` proposal. Apply increments both version and conf version, writes `MergeState`, flushes, and creates the merge-source checkpoint if missing. Peer apply result installs the new metadata, persists region state through state changes, enters prepare-merge mode, resolves any waiting catch-up logs, and starts commit merge.

## State And Persistence Behavior
Prepare merge persists `RegionLocalState` with `PeerState::Merging`, updated epoch, `MergeState { min_index, target, commit }`, and a source checkpoint at `merge_source_path(region_id, log_index)`. It also sets pessimistic lock status to `MergingRegion` while locks are transferred and resumes/cleans it on failure or rollback. In-memory state in `MergeContext` tracks async checks and is reconstructed from persisted state after restart only once apply has made the prepare durable.

## Dependencies And Integration Points
Depends on raft progress and log storage, `SimpleWriteReqDecoder` for scanning log payloads, lock CF serialization, tablet checkpointers, pre-flush infrastructure in admin/mod.rs, availability extra messages, `ProposalContext::PREPARE_MERGE`, `ProposalControl`, transaction lock tables, and commit merge startup.

## Risks And Edge Cases
Merge is rejected for dirty source tablets, missing/stale target metadata, non-sibling ranges, mismatched peer store sets, pending snapshots, excessive log gap, conf changes or epoch-changing admin logs in the gap, oversized embedded entries, and oversized pessimistic locks. The trim check has a timeout cleanup path because request ownership crosses callbacks. Failure after lock status changes must call `post_prepare_merge_fail` to return locks to normal.

## Test Signals
No local unit tests are defined here, but the file includes failpoints and extensive assertions. Integration signals include `prepare_merge` metrics, `PendingPrepareMerge` retry behavior, persisted `PeerState::Merging`, checkpoint creation, proposal rejection in merging mode, and subsequent `start_commit_merge`.
