<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ClosingContainerHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ClosingContainerHandler.java

## Purpose

`ClosingContainerHandler` handles SCM containers in `CLOSING` state. It sends close commands to non-unhealthy replicas, transitions all-unhealthy closing containers, and eventually closes empty containers that never acquired replicas.

## Important APIs, Types, and Functions

The main method is `handle`; `hasWaitTimeElapsed` computes the empty-closing grace period as replication-manager interval times five. It uses `sendCloseContainerReplicaCommand`, `updateContainerState`, `LifeCycleEvent.QUASI_CLOSE`, `CLOSE`, and `ContainerHealthState.MISSING`.

## Control Flow

Non-closing containers pass through. Empty replica sets are sampled as missing. Read-only mode returns after classification. For each non-unhealthy replica, it sends a close command, force-closing non-Ratis replicas. If all replicas are unhealthy, Ratis moves to quasi-closed and EC moves to closed. If there are no replicas, no keys, and the wait time has elapsed, it closes the container.

## State and Persistence Behavior

It uses the container's `stateEnterTime` and a `Clock` to determine elapsed time. Command sends are transient; `updateContainerState` changes SCM container metadata through the normal state machine.

## Dependencies and Integration Points

It integrates with ReplicationManager, container lifecycle events, safe/read-only scanning, and the broader health chain that should not run replication repairs on still-closing containers.

## Risks and Edge Cases

The all-unhealthy branch treats EC differently from Ratis. Empty containers require both no replicas and zero key count to avoid premature close. Clock or interval misconfiguration can delay cleanup or close too early.

## Test Signals

Tests should assert close command issuance for non-unhealthy replicas, no command for unhealthy replicas, all-unhealthy Ratis/EC transitions, read-only no mutation, empty missing sampling, and grace-period close for empty no-replica containers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ClosingContainerHandler.java -->
