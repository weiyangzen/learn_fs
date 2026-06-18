# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/merge/commit.rs

## Purpose
Implements the commit half of raftstore-v2 region merge. Source peers that have applied `PrepareMerge` ask the target peer to propose `CommitMerge`; target apply merges the source checkpoint tablet and target tablet into a new target tablet, then the source peer is destroyed after catch-up and acknowledgement.

## Important APIs, Types, And Functions
`CommitMergeResult` carries target apply side effects back to the peer FSM: applied index, prepare-merge index, source checkpoint path, new region state, source region, source safe-ts, and the newly opened tablet. `CatchUpLogs` is the pause/response channel used when target apply must redirect source entries before it can finish. `MERGE_IN_PROGRESS_PREFIX` and `MergeInProgressGuard` create a marker directory that distinguishes recoverable partial merged tablets from completed ones. Main peer methods are `start_commit_merge`, `on_check_merge`, `ask_target_peer_to_commit_merge`, `on_ask_commit_merge`, `propose_commit_merge`, `on_redirect_catch_up_logs`, `on_catch_up_logs`, `finish_catch_up_logs`, `on_apply_res_commit_merge`, and `on_ack_commit_merge`.

## Control Flow
After source apply of `PrepareMerge`, `start_commit_merge` schedules/checks merge and builds an `AskCommitMerge` request for the local target peer. The request embeds source `RegionLocalState` plus source raft entries from the minimum replicated index through the prepare commit. The target rejects stale epochs, ignores lagging epochs, short-circuits already merged records, and otherwise proposes a `CommitMerge` admin log with `ProposalContext::COMMIT_MERGE`. During target apply, if the source checkpoint is not yet present, apply redirects `CatchUpLogs` to the source peer and waits on a oneshot. The source appends/commits missing merge entries if necessary, applies up to `PrepareMerge`, returns safe-ts, and marks itself for destroy. The target then extends its range, merges tablets, records a `MergedRecord`, and reports `CommitMergeResult`; peer-side handling installs metadata, safe-ts, read tablet, tombstones old tablets, forces split-stat refresh, and notifies PD if leader.

## State And Persistence Behavior
Persistence is tablet-oriented. The source checkpoint lives at `merge_source_path(source_id, prepare_index)` and is consumed by target apply. Target apply opens a new tablet at `tablet_path(target_id, commit_index)`, using `MergeInProgressGuard` to delete incomplete output after crashes and defuse the marker only after `tablet.merge` succeeds. `RegionLocalState` is updated to `Normal`, new tablet index, widened key range, and appended merged records. Peer-side `state_changes_mut().put_region_state` and `apply_trace_mut().on_admin_flush` make the new state durable through raftstore-v2 state change flushing.

## Dependencies And Integration Points
Depends on merge preparation state from `prepare.rs`, `merge_source_path` from `merge/mod.rs`, raft log storage and `maybe_append`, tablet registry/factory merge support, `StoreContext` routing/control messages, `SharedReadTablet`, transaction context safe-ts merge, PD heartbeat/GC peer ticks, and proposal contexts understood by raftstore.

## Risks And Edge Cases
Correctness relies on source and target regions being siblings on the same stores, source dirty data being trimmed before commit, no oversized embedded entry payload, and precise safe-ts transfer before source metadata disappears. Crash recovery depends on marker-directory semantics and idempotent reuse of existing merged tablets. Empty catch-up entries can still need a commit-index bump, and term advancement is handled manually when appending logs outside normal raft replication.

## Test Signals
The file contains many failpoints for scheduling, proposing, source checkpoint acquisition, merge execution, and apply result handling. There are no local unit tests in this file; coverage is integration-style through merge tests elsewhere plus invariants, panics, metrics counters, PD heartbeats, tombstone cleanup, and source peer destruction.
