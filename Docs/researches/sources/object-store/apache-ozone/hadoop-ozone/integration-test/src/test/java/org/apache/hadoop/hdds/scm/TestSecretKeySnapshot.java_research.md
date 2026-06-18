# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSecretKeySnapshot.java

## Purpose

`TestSecretKeySnapshot` verifies that SCM symmetric secret keys are transferred to a lagging HA follower through snapshot installation and continue to synchronize after the follower rejoins.

## Important APIs, Types, And Functions

The test creates a secure MiniKdc-backed Ozone HA cluster with block tokens enabled, short secret-key rotation durations, snapshot threshold/purge settings, and one inactive SCM. It uses `SecretKeyManager`, `ManagedSecretKey`, `SCMStateMachine`, `StorageContainerManager`, and helper `writeToIncreaseLogIndex`.

## Control Flow

Setup configures Kerberos principals/keytabs, starts two active SCMs plus an inactive SCM, and waits for readiness. The test waits until the leader has rotated keys, advances the Ratis log via container allocations, starts the inactive follower, waits for its state machine to apply the snapshot, then compares follower keys with leader keys and verifies later rotations replicate normally.

## State And Persistence Behavior

The central persistent state is SCM's secret-key table, Ratis log, snapshot checkpoint, and container allocation records used to advance log index. Follower state is restored from snapshot while it missed live rotations.

## Dependencies And Integration Points

It integrates MiniKdc security setup, block-token secret key management, SCM HA snapshot install, Ratis state-machine indexes, and container manager mutations.

## Risks And Test Signals

Failures indicate missing secret-key table data in snapshots, follower pause/catch-up problems, or post-snapshot replication breakage. Time-based key rotation and security setup are flakiness risks.
