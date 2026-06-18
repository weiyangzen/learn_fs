# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMInstallSnapshotWithHA.java

## Purpose

`TestSCMInstallSnapshotWithHA` verifies SCM Ratis snapshot installation in a three-SCM HA cluster, including normal follower catch-up and rejection of old or corrupted checkpoints. The class is marked flaky for HDDS-5631.

## Important APIs, Types, And Functions

Setup configures SCM HA snapshot threshold and raft-log purge gap, starts a MiniOzone HA cluster with two active SCMs and one inactive SCM. Tests use `StorageContainerManager`, `SCMHAManagerImpl`, `SCMStateMachine`, `SCMMetadataStore`, `SCMDBDefinition`, `ContainerInfo`, `GenericTestUtils`, and a `DummyExitManager`. Helper `writeToIncreaseLogIndex` allocates containers until a target log index is reached.

## Control Flow

`testInstallSnapshot` advances the leader log, starts the inactive SCM, and waits for snapshot installation to bring it up to date. Failure tests attempt installing an old checkpoint or a corrupted checkpoint and assert errors/logging/exit behavior rather than successful catch-up.

## State And Persistence Behavior

The tests mutate SCM Ratis logs, snapshots, metadata tables, and container allocation records. Follower state is rebuilt from snapshots, and corrupted/old checkpoint paths validate persistence safeguards.

## Dependencies And Integration Points

It integrates SCM HA Ratis, snapshot purge/install logic, metadata store checkpointing, container allocation, and process-exit handling.

## Risks And Test Signals

Failures indicate follower catch-up gaps, snapshot-index validation bugs, checkpoint corruption handling regressions, or unsafe process-exit behavior. Timing and log-purge thresholds are sensitive.
