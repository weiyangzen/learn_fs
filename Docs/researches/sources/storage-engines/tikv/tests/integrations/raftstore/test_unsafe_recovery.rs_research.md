# sources/storage-engines/tikv/tests/integrations/raftstore/test_unsafe_recovery.rs

## Purpose
This file validates unsafe recovery and force-leader behavior when raft quorum is lost. It covers demoting failed voters, removing failed learners, auto-promoting survivors, joint-state recovery, region create/tombstone plans, force-leader safety gates, snapshots during recovery, uncommitted conf changes, stale forced leaders, repeated force-leader commands, merge-aware reporting, and commit-index forwarding while ignoring learners.

## Important APIs, Types, and Functions
Key APIs include `cluster.must_enter_force_leader`, `enter_force_leader`, `exit_force_leader`, `pd_client.must_set_unsafe_recovery_plan`, `must_send_store_heartbeat`, `pdpb::RecoveryPlan`, `DemoteFailedVoters`, `metapb::Region`, `ConfChangeType`, `MessageType`, and `find_peer`. Local macros `confirm_quorum_is_lost!` and `must_get_error_recovery_in_progress!` encode important recovery invariants.

## Control Flow
Most tests build a multi-node region, split to isolate a target key range, transfer leadership, stop enough nodes to lose quorum, confirm proposals fail, enter force-leader on a surviving store, apply a PD recovery plan or manual peer removal, exit force-leader, and then assert normal writes resume. Specific flows test invalid demotion plans, learner promotion, joint-conf exit, creating replacement regions, reentrant create/destroy plans, forced leaders on learners or hibernated peers, snapshot catch-up before recovery commits, uncommitted conf changes, healthy-region misuse, stale chosen leaders, repeated force-leader attempts, multi-election recovery, and merge ordering hazards.

## State and Persistence Behavior
The tests inspect PD region metadata, peer roles, store reports, raft local hard-state commit/last index, and persisted key visibility. They verify that force leader forbids normal reads/writes/read-index while recovery is in progress, failed voters become learners, failed learners can be removed, created regions become queryable, tombstoned regions report correctly, and commit index can advance without counting stopped learners as required voters.

## Dependencies and Integration Points
This file integrates raft leader election, joint consensus, PD unsafe recovery plans/reports, store heartbeat reporting, merge protocol, snapshot catch-up, hibernation, raft log commit-index rules, and both v1/v2 node clusters for many scenarios.

## Risks
Unsafe recovery is deliberately dangerous. Regressions can cause split brain, data loss, recovery deadlock, incorrect PD reports, unsafe merge ordering, or writes allowed while the system is still in force-leader state. Many tests manipulate timing and node restarts, so lease expiration and election waits are critical.

## Test Signals
Signals include failed proposals before recovery, `RecoveryInProgress` errors during force-leader, exact peer-role counts in PD metadata, nonempty and correct store reports, successful writes only after exit, absence of stale data from uncommitted writes, `has_commit_merge` report fields, and hard-state commit index advancing beyond the previous last index in learner-ignored recovery.
