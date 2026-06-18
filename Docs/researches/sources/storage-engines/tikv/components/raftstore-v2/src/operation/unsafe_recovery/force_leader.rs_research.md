# sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/force_leader.rs

Purpose: this file implements the unsafe recovery force-leader state machine, allowing one surviving peer to temporarily become leader without normal quorum so it can commit recovery configuration changes.

Important APIs/functions: Peer methods include `on_enter_pre_force_leader`, `on_force_leader_fail`, `on_enter_force_leader`, `on_exit_force_leader`, `on_exit_force_leader_campaign`, `check_force_leader`, and `maybe_force_forward_commit_index`. Helper `get_force_leader_expected_alive_voter` filters voters by failed stores.

Control flow: entering pre-force-leader first handles existing force-leader state, rejects uninitialized peers, and may wait election ticks so leader lease/check-quorum can expire. It rejects if expected alive voters still form quorum. It disables prevote, campaigns, verifies self vote, and stores `ForceLeaderState::PreForceLeader`. `check_force_leader` later waits near election timeout, validates votes only from expected alive voters, and if all grant, synthesizes vote responses from failed-store voters to transition raft to leader. In force-leader state, it disables check quorum and may advance commit index to the minimum matched/persisted index among non-failed stores when the term matches. Exiting restores follower role, check quorum, prevote, and optionally schedules a fresh campaign.

State and persistence: force leadership is an in-memory `ForceLeaderState`; raft term/vote/role/check-quorum/prevote fields are mutated directly. Commit advancement changes raft log committed index and requires ready processing via `set_has_ready`.

Dependencies/integration: depends on raft `RawNode` internals, progress tracker votes, `LeaseState`, unsafe recovery state, peer router campaign message, and store config election ticks.

Risks: the code deliberately violates normal raft election rules; incorrect failed-store input can create split brain. Lease expiration checks guard stale leaders, but clock/tick assumptions matter. Commit forwarding refuses previous-term logs, reducing but not eliminating recovery hazards. `WaitForceCompact` is marked unreachable in v2 paths.

Test signals: no direct tests in this file. Coverage should be in unsafe recovery force-leader integration and failover tests.
