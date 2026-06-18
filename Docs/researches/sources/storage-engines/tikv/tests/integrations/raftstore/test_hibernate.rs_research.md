# sources/storage-engines/tikv/tests/integrations/raftstore/test_hibernate.rs

Purpose: verifies hibernate-region behavior: proposals waking sleeping peers, learner/voter transitions, delayed transfer and split handling, mixed configuration/version gating, joint-state demotion recovery, quorum hibernation with down peers, and matched-peer quorum checks.

Important APIs and functions: `must_wait_until_hibernated` polls `unstable_entries_state` until `GroupState::Idle`. `make_cb`, `make_write_req`, and `CbReceivers` build proposed callbacks for low-level async command assertions. Tests rely heavily on `configure_for_hibernate`, raft message filters, `GroupState`, PD peer changes, and leader transfer.

Control flow: scenarios start hibernate-enabled clusters, force replication, wait for sleep using election-time-derived intervals, then inject proposals, reads, conf changes, splits, delayed transfer messages, or node restarts. Quorum tests stop voters/learners, wait for down-peer detection, and monitor outbound messages with callbacks to decide whether a leader stayed asleep or awake.

State and persistence: validates key replication after wakeup, PD peer roles, raft log truncation state, hibernated group state, down-peer detection, leader identity after demotion/recovery, and persisted data after learners catch up by log or snapshot.

Dependencies and integration points: integrates raftstore hibernate logic, raft message types (`MsgTransferLeader`, `MsgTimeoutNow`, append/heartbeat responses), PD version gates, joint consensus, snapshot/log compaction, node/server clusters, and callback-based proposal plumbing.

Risks: highly timing-sensitive because hibernation, leader election, down-peer detection, and max-peer-down durations are all time based. Message filters must be cleared carefully. Feature-gate behavior depends on PD cluster version strings. Several assertions monitor absence of sends, which can be susceptible to scheduler jitter.

Test signals: hibernated leaders do not send heartbeats while sleeping, proposals/read-index/conf-change wake and complete, learners catch up after restart or snapshot, leaders stay awake when peers do not support hibernate or matched quorum is insufficient, and leaders can still hibernate when a down voter/learner is safe under quorum rules.
