# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestStorageContainerManagerHAWithAllRunning.java

## Purpose

`TestStorageContainerManagerHAWithAllRunning` validates that a fully running SCM HA ensemble stays synchronized while serving client writes. It checks all SCM roles, applied indexes, and HA metrics after data-plane activity.

## Important APIs, Types, And Functions

The abstract class implements `HATests.TestCase`, using the provided HA cluster. It relies on Ozone object-store put-key helpers, `StorageContainerManager`, SCM Ratis role/state access, and metric validation helpers. Key helpers are `doPutKey`, `getLastAppliedIndex`, `areAllScmInSync`, `assertRatisRoles`, and `checkSCMHAMetricsForAllSCMs`.

## Control Flow

`testAllSCMAreRunning` verifies all SCMs are active, writes a key through OM/client paths, waits until followers catch up to the leader's last-applied index, then validates Ratis roles and metrics across the ensemble.

## State And Persistence Behavior

The test persists a key, SCM allocation metadata, and replicated SCM Ratis log entries. It observes volatile role state and durable applied indexes on each SCM.

## Dependencies And Integration Points

It integrates HA test fixtures, Ozone client writes, OM-to-SCM allocation, SCM Ratis replication, and SCM HA metrics.

## Risks And Test Signals

Failures point to follower lag, missing replicated SCM metadata, role confusion, or incorrect HA metrics. The synchronization wait depends on Ratis progress and cluster load.
