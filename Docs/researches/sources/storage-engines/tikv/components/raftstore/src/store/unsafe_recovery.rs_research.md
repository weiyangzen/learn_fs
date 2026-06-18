# sources/storage-engines/tikv/components/raftstore/src/store/unsafe_recovery.rs

## Purpose

Defines the raftstore side of PD-driven online unsafe recovery. It routes force-leader and recovery-plan commands to peers/store FSMs, models force-leader and unsafe-recovery peer states, coordinates multi-peer phases through drop-triggered syncers, collects peer reports into store reports, and builds raft admin requests for exiting joint state and demoting failed voters.

## Important APIs, Types, And Functions

`UnsafeRecoveryHandle` is the orchestration interface used by PD worker/recovery code. It can send enter-force-leader, create-peer, destroy-peer, demote-peers, broadcast wait-apply, broadcast fill-out-report, broadcast exit-force-leader, and send a final store report. The `Mutex<RaftRouter>` implementation converts these into `SignificantMsg` or `StoreMsg` variants, using force send for store-level recovery messages and treating destroy of an already missing region as success.

`ForceLeaderState` models force-leader progression: `WaitTicks`, `WaitForceCompact`, `PreForceLeader`, and `ForceLeader`. `InvokeClosureOnDrop` runs a boxed closure when the last shared reference drops. `UnsafeRecoveryForceLeaderSyncer`, `UnsafeRecoveryExecutePlanSyncer`, `UnsafeRecoveryWaitApplySyncer`, and `UnsafeRecoveryFillOutReportSyncer` are cloneable phase coordinators. `UnsafeRecoveryState` is per-peer recovery state: `WaitApply`, `DemoteFailedVoters`, `Destroy`, `WaitInitialize`, and `Failed`, with `check_timeout`, `is_abort`, and `abort`. `exit_joint_request` and `demote_failed_voters_request` build raft admin requests for recovery plan execution.

## Control Flow

Unsafe recovery proceeds in phases documented in the file. Report phase starts with `start_unsafe_recovery_report`, which creates a wait-apply syncer and broadcasts `UnsafeRecoveryWaitApply`. When all peer-held wait-apply syncer clones drop, the closure optionally broadcasts exit-force-leader, creates a fill-out-report syncer, and broadcasts `UnsafeRecoveryFillOutReport`. Each peer reports itself into the shared vector; when the last fill-out-report syncer drops, the closure builds a `StoreReport`, sets the report step, and schedules it through `send_report`.

Force-leader phase creates `UnsafeRecoveryForceLeaderSyncer`; when all target peers finish entering force leader and drop it, its closure starts a new report without exiting force leader. Plan execution uses `UnsafeRecoveryExecutePlanSyncer`; when all create/destroy/demote operations drop the syncer without abort, its closure starts a report with `exit_force_leader = true`. If any execution path calls `abort`, the shared flag prevents the drop closure from scheduling the next report. Peer FSM code consumes `UnsafeRecoveryState` to wait for apply indexes, destroy peers, initialize created peers, demote failed voters, and handle timeout/abort.

`demote_failed_voters_request` creates a `ChangePeerV2` admin request: failed voters become learners, failed learners are removed, and the local peer is promoted to voter if it is currently learner. It returns `None` when no changes are needed. `exit_joint_request` builds an empty `ChangePeerV2` request to leave joint consensus before demotion when required.

## State And Persistence Behavior

This file owns in-memory coordination state only. Long-lived recovery progress is represented by peer/store FSM state and PD reports outside this file. Syncer state is reference-counted; progress to the next phase depends on all relevant clones being dropped. Abort flags are shared `Arc<Mutex<bool>>`, and report collection is an `Arc<Mutex<Vec<PeerReport>>>`. The generated raft admin requests are persisted only when later proposed and applied by raftstore.

## Dependencies And Integration Points

Depends on raftstore routing (`RaftRouter`, `SignificantRouter`, `PeerMsg`, `StoreMsg`, `SignificantMsg`), peer FSM/admin helpers (`new_admin_request`, `new_change_peer_v2_request`), kvproto PD and metapb recovery/report/change-peer types, raft `ConfChangeType`, and `collections::HashSet`. PD worker code constructs the syncers and calls `UnsafeRecoveryHandle`; peer FSM code handles the corresponding significant messages and uses `ForceLeaderState`, `UnsafeRecoveryState`, `exit_joint_request`, and `demote_failed_voters_request`.

## Risks

The drop-driven coordination is compact but fragile: leaked syncer clones stall phases, and premature drops can advance phases before peer work really finished. Abort only suppresses future closure action; it does not undo already sent peer/store messages. Force leader intentionally bypasses normal raft safety assumptions for recovery, so message routing, failed-store sets, and demotion request construction must be exact. `demote_failed_voters_request` contains a duplicated `let mut cp` inside the learner removal branch, which is harmless after shadowing but easy to misread. The request builder assumes the supplied `failed_voters` and `region.peers` roles are current enough for the recovery plan. `send_destroy_peer` treats missing regions as success, which is correct for idempotent destruction but could hide an unexpected region-id mismatch.

## Test Signals

There are no local unit tests in this file. Regression coverage should come from PD worker and peer FSM unsafe-recovery tests that enter force leader, wait for apply, create peers, destroy peers, demote failed voters from joint and non-joint states, abort timed-out states, collect reports, and verify generated `ChangePeerV2` requests. Runtime logs around phase completion/abort and PD `StoreReport` contents are important operational signals.
