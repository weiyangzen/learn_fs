<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_replication_mode.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_replication_mode.rs

## Purpose
This file tests DR Auto Sync and majority replication mode behavior: label-aware commit safety, sync-recover, async switching, conf-change checks, group-id assignment, hibernate interaction, migration between replication modes, rolling label loading, and commit-group deadlock avoidance.

## Important APIs, Types, and Functions
Helper functions `prepare_cluster`, `configure_for_snapshot`, `run_cluster`, and `prepare_labels` configure labeled server clusters. Tests use PD APIs `configure_dr_auto_sync`, `switch_replication_mode`, `region_replication_status`, `must_joint_confchange`, `must_leave_joint`, `transfer_leader`, and conf-change helpers with `ConfChangeType`.

The file uses `RegionReplicationState::{IntegrityOverLabel, SimpleMajority}`, `DrAutoSyncState::{Async, SyncRecover}`, isolation filters, snapshot-forcing raft log GC settings, and async command callbacks.

## Control Flow and Behavior
Tests isolate stores in specific zones to verify writes commit only when label integrity can be satisfied. Switching tests move from sync to async to sync-recover and assert write blocking/unblocking and replication status IDs. Snapshot tests force log truncation, switch modes, restore an isolated store by snapshot, and verify the status returns to label integrity after apply.

Conf-change tests validate promotion decisions under DR label constraints. Migration tests configure DR mode at runtime, switch to majority and back, split regions created under majority, and verify both old and new regions report updated DR status. Rolling-start tests add labels before each node start to confirm labels are loaded into store metadata. The commit-group migration test uses failpoints around snapshot/apply peer creation to ensure assigning commit groups while regions migrate does not deadlock.

## State and Persistence
The tests observe PD replication status state IDs, replication state values, committed key visibility, snapshot catch-up, group IDs implied by commit behavior, label metadata loaded during rolling starts, and liveness of peer creation under failpoint stalls.

## Dependencies and Integration Points
This suite integrates PD replication mode configuration, store labels, raft conf change including joint consensus, snapshot/log GC, async write callbacks, hibernation, and raftstore-v2 commit group assignment.

## Risks
Regressions include writes committing without required label durability, writes blocking after async mode should unblock, sync-recover incorrectly blocking, label metadata missing after rolling starts, unsafe peer promotion, stale replication status after split/migration, and deadlocks while assigning commit groups during snapshot application.

## Test Signals
Signals are callback timeout/success, exact replication state and state_id assertions, key presence on specific engines, successful leave-joint operations, successful leader transfers after group-id updates, and both migrated regions reporting `IntegrityOverLabel`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_replication_mode.rs -->
