# sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/report.rs

Purpose: this file handles unsafe recovery reporting and wait-for-apply/report-status peer operations.

Important APIs/functions: `Store::on_unsafe_recovery_report` sends a store heartbeat with an optional recovery report. Peer methods include `on_unsafe_recovery_wait_apply`, `unsafe_recovery_maybe_finish_wait_apply`, `on_unsafe_recovery_fill_out_report`, and `check_unsafe_recovery_state`.

Control flow: wait-apply rejects conflicting non-aborted states, chooses target index as last index in force-leader mode or committed index otherwise, and records `UnsafeRecoveryState::WaitApply` until applied catches up or serving is gone. Fill-out report gathers raft state and region state, marks force-leader status, scans uncommitted entries for `COMMIT_MERGE` proposal context, and reports through the syncer. The periodic checker advances wait-apply, wait-initialize, and demote states.

State and persistence: no writes are performed here except through state clearing. The report serializes current raft local state and region local state into PD protobufs, plus derived flags.

Dependencies/integration: depends on raft `Storage::entries`, `ProposalContext`, PD report protobufs, unsafe recovery syncers, and the demotion/create modules through checker calls.

Risks: scanning uncommitted entries panics on storage errors; recovery reporting assumes raft log access is reliable. Wait targets differ in force-leader mode because proposed logs are expected to become committed by force-forwarding.

Test signals: no local tests. Integration tests should verify reports include commit-merge and force-leader markers and that wait states clear only after apply.
