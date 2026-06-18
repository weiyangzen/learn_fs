# sources/storage-engines/tikv/tests/integrations/raftstore/test_flashback.rs

Purpose: tests raftstore flashback mode semantics across v1/v2 clusters: pessimistic lock handling, read/write gating, scheduling blocks, split/conf-change races, local reads, persisted flashback metadata, snapshot propagation, and helper request behavior.

Important APIs and functions: `eventually_meet` polls async lock-state changes. `ClusterI` abstracts node-cluster and raftstore-v2 cluster methods. `must_check_flashback_state`, `request`, `must_request_with_flashback_flag`, `must_request_without_flashback_flag`, and error assertion helpers centralize command construction and flashback flag handling. Tests use `AdminCmdType::PrepareFlashback` and `FinishFlashback`, `WriteBatchFlags::FLASHBACK`, and `SnapContext { allowed_in_flashback: true }`.

Control flow: tests create clusters, transfer a known leader, optionally pause apply with failpoints, send flashback admin commands, and then issue read/write/status/schedule/split/conf-change/snapshot flows with or without the flashback flag. Snapshot tests isolate a peer before or during flashback to verify flashback state catches up when snapshots are applied.

State and persistence: checks in-memory pessimistic lock table status, `RegionLocalState.region.is_in_flashback`, raft local indexes for local-read side effects, command error headers, region epoch/peer metadata after split/conf-change, and follower state after snapshot catchup.

Dependencies and integration points: integrates raftstore flashback admin command handling, transaction lock memory extension, raft command flags, snapshot context, failpoints, region status commands, split/conf-change machinery, and both raftstore engines.

Risks: failpoint-gated race tests are sensitive to batching behavior. Local-read assertions depend on exact raft index increments. Flashback flag semantics are security-sensitive: accidental allowance of unflagged writes/reads during flashback would violate intended isolation.

Test signals: unflagged reads/writes fail with `flashback_in_progress` during prepared flashback, flagged requests succeed only when appropriate, unprepared flashback requests return `flashback_not_prepared`, scheduling operations are blocked, persisted flashback state toggles on prepare/finish, and isolated peers converge to correct state after snapshots.
