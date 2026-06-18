# sources/storage-engines/tikv/components/snap_recovery/src/leader_keeper.rs

Purpose: repeatedly forces and verifies raft leadership for selected regions during snapshot recovery.

Important APIs and types: `LeaderKeeper<'a, EK, Router>` stores a router and `not_leader` region set. `StepResult` reports `failed_leader` checks and `campaign_failed` sends. `elect_and_wait_all_ready` loops until all regions verify as leaders. `step` checks and campaigns in chunks of 256.

Control flow: `step` snapshots pending regions, for each batch asynchronously checks leader readiness by sending `SignificantMsg::LeaderCallback`. If the callback response has an error, it records failed leader and sends a casual `Campaign(ForceLeader)` message. Successfully checked regions are removed from `not_leader`. `elect_and_wait_all_ready` logs each step, waits 10 seconds via global timer, and returns when no failed leaders remain.

State and persistence behavior: only in-memory pending-region state. Actual raft leadership is changed through raftstore router messages.

Dependencies and integration points: used by `RecoveryService::recover_region`. Depends on raftstore `CasualRouter`, `SignificantRouter`, callbacks, global timer, and `KvEngine` snapshot type.

Risks: convergence depends on raftstore accepting force campaigns and callbacks. Missing regions remain pending and campaign failures are retried. The loop exits only when `failed_leader` is empty, so persistent router/store failures can hang recovery. Debug formatting intentionally truncates long result lists.

Test signals: `test_basic`, `test_failure`, and `test_many_regions` use a mock router to verify first-step campaigns, handling of missing regions, eventual success after region insertion, and batching beyond 2048 regions.
