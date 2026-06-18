# sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/demote.rs

Purpose: this file demotes failed voters during unsafe recovery after a peer has entered force-leader mode, restoring a valid quorum configuration.

Important APIs/functions: Peer methods are `on_unsafe_recovery_pre_demote_failed_voters`, `unsafe_recovery_demote_failed_voters`, and `unsafe_recovery_maybe_finish_demote_failed_voters`.

Control flow: pre-demotion rejects concurrent non-aborted recovery state and requires `is_in_force_leader`. If the region is already in joint state, it first proposes an `exit_joint_request`, then stores `UnsafeRecoveryState::DemoteFailedVoters` with `demote_after_exit=true` and target last index. Otherwise it constructs `demote_failed_voters_request`, proposes it as an admin command, and stores a demotion wait state with target last index. The check method waits until raft applied reaches the target. If it was only exiting residual joint state, it re-enters demotion; otherwise it may issue a final exit-joint command and clears state.

State and persistence: the actual configuration changes are raft admin commands. The unsafe recovery state records the syncer, failed voters, target index, and whether a second-stage demotion is needed after exiting joint state. Errors may set `UnsafeRecoveryState::Failed`.

Dependencies/integration: depends on raftstore helper constructors `demote_failed_voters_request` and `exit_joint_request`, `CmdResChannel` for immediate command response inspection, force-leader state from `force_leader.rs`, and periodic `check_unsafe_recovery_state` from `report.rs`.

Risks: losing force leadership between exit-joint and demotion aborts progress. Immediate `try_result` only observes synchronous command errors; later apply failures are represented by waiting/apply state. Joint-state transitions are multi-stage and must preserve target indexes to avoid clearing state before commands apply.

Test signals: no direct tests here. It should be covered by unsafe recovery and joint-consensus integration tests.
