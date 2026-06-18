# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/mod.rs

## Purpose
Central admin-command dispatcher for raftstore-v2 peers. It validates, routes, proposes, and post-processes admin commands such as split, compact log, conf change, transfer leader, merge, flashback, and GC peer updates.

## Important APIs, Types, And Functions
`AdminCmdResult` is the apply-to-peer side-effect enum consumed by `command/mod.rs`. `Peer::on_admin_command` is the main entry point. `on_prepare_merge` adjusts raft inflight behavior for merge under disk pressure. `start_pre_flush` schedules tablet flushes and sends `MsgFlushMemtable` extra messages to follower voters. The module re-exports merge and split helpers including `MergeContext`, `CatchUpLogs`, `SplitInit`, `SplitFlowControl`, and tablet path helpers.

## Control Flow
`on_admin_command` rejects non-serving peers and non-admin requests, invokes coprocessor pre-propose hooks, validates store/peer/term/epoch through `validate_command`, checks disk-full policy except for transfer-leader warmup and conf changes, and requires applied-to-current-term for most admin commands. It delays conflicting commands through `ProposalControl`, rejects most proposals during pending/applied prepare merge, triggers merge-specific disk-full handling, drains pending simple writes to preserve ordering, then dispatches by `AdminCmdType`. Batch split performs an asynchronous pre-flush phase before reproposing with `PRE_FLUSH_FINISHED`. Transfer leader either runs the warmup protocol or proposes a flagged transfer-leader log. Merge, flashback, compact log, conf change, and GC updates delegate to their submodules or raw `propose`.

## State And Persistence Behavior
This file mainly coordinates proposal state rather than applying persistence. Successful admin proposals are recorded in `ProposalControl` and may disable commit broadcast skipping until uncommitted admin work is resolved. `start_pre_flush` can cause tablet memtables to flush before split or merge proposals, reducing checkpoint cost and improving availability under disk pressure.

## Dependencies And Integration Points
Integrates with `StoreContext`, coprocessor host, raft metrics, `ProposalControl`, write batching, split/merge/flashback/conf-change submodules, disk-full peer context, router mailbox resubmission, tablet scheduler, and raft extra messages.

## Risks And Edge Cases
Admin ordering depends on draining pending writes before proposing admin logs. Merge mode rejects most commands to protect source-region invariants. Batch split and prepare/commit merge use callbacks through router mailboxes, so shutdown paths must tolerate missing mailboxes. Disk-full logic intentionally allows transfer leader, conf change, and merge-related flows under narrower rules.

## Test Signals
No tests are local to this file. Signals are covered by submodule tests and integration behavior: proposal metrics, delayed conflict callbacks, admin result handling, pre-flush resubmission, disk-full rejection paths, and fail-fast panics for unimplemented admin types.
