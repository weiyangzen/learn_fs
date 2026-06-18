# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/control.rs

## Purpose
Provides proposal conflict control for raftstore-v2, replacing the older epoch checker by tracking proposed/admin-applied lifetimes and merge-mode gating.

## Important APIs, Types, And Functions
`ProposedAdminCmd` records admin type, committed flag, epoch-change state, raft index, and delayed response channels. `ProposalControl` stores a small ordered list of proposed admin commands, pending prepare-merge flag, applied prepare-merge index, and current term. Key methods are `maybe_update_term`, `check_conflict`, `record_proposed_admin`, `commit_to`, `advance_apply`, `set_pending_prepare_merge`, `enter_prepare_merge`, `leave_prepare_merge`, `is_splitting`, and `is_merging`.

## Control Flow
Before proposing normal or admin work, callers use `check_conflict` with either no admin type or an admin type. The method compares the candidate's epoch checks against already proposed admin commands and treats `PrepareMerge` as a universal conflict. Conflicting callbacks are delayed instead of immediately failed. Once raft commits indexes, `commit_to` marks proposed admins as committed and can trigger hooks. Once apply reaches indexes, `advance_apply` returns delayed channels with epoch-not-match responses based on the current region. Term increases stale all delayed work and clear the queue.

## State And Persistence Behavior
All state is in memory and rebuilt from peer/apply state after restart. The applied prepare-merge index mirrors durable merge state and makes `is_merging` true even after the proposal queue has advanced. Dropping `ProposalControl` notifies delayed callbacks with stale-command errors to avoid hanging clients.

## Dependencies And Integration Points
Uses raftstore admin epoch lookup, normal request epoch-check flags, `CmdResChannel`, apply notification helpers, and `AdminCmdType`. It is called by admin dispatch, simple-write handling, apply result advancement, merge prepare/rollback, and split status checks.

## Risks And Edge Cases
Correctness depends on recording only epoch-changing admin commands and maintaining increasing indexes. Term regression panics. Delayed callbacks intentionally receive epoch-not-match after the conflicting admin applies, encouraging clients to refresh region metadata instead of retrying with blind backoff.

## Test Signals
`test_proposal_control` covers conflict detection, commit/apply transitions, delayed callback delivery, term-change stale responses, and drop cleanup. `test_proposal_control_merge` covers prepare-merge committed state, applied merge mode, and leaving merge mode.
