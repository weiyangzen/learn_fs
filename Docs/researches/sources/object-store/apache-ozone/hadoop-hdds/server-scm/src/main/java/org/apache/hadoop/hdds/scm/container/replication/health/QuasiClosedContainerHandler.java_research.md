<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/QuasiClosedContainerHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/QuasiClosedContainerHandler.java

## Purpose

`QuasiClosedContainerHandler` handles Ratis containers in `QUASI_CLOSED` state. It force-closes safe candidates and reports stuck quasi-closed containers that cannot be force-closed without risking data loss.

## Important APIs, Types, and Functions

Important methods are `handle`, static `isQuasiClosedStuck`, private static `canForceCloseContainer`, and `forceCloseContainer`. It sends close commands through `ReplicationManager.sendCloseContainerReplicaCommand` and reports `ContainerHealthState.QUASI_CLOSED_STUCK`.

## Control Flow

The handler ignores non-Ratis and non-quasi-closed containers. `canForceCloseContainer` requires at least one quasi-closed replica, the max quasi-closed sequence ID to be at least the max unhealthy sequence ID, and enough unique origins among quasi-closed or unhealthy replicas to meet the replication factor. When safe, it force-closes quasi-closed replicas with the highest sequence ID; otherwise it samples stuck state. It always returns `false`.

## State and Persistence Behavior

It owns no persistent state. Close commands eventually move replicas/container forward. Report sampling records stuck state without changing metadata.

## Dependencies and Integration Points

It integrates with Ratis replication checks, quasi-closed-stuck replication checks, origin-datanode tracking, sequence IDs, and ReplicationManager close command dispatch.

## Risks and Edge Cases

The safety rule intentionally leaves some containers stuck forever if unique origins are permanently lost. Including unhealthy origins prevents closing if an unhealthy replica may have newer data. Returning `false` permits replication health checks to run afterward.

## Test Signals

Tests should cover safe force close at highest BCSID, unsafe due to insufficient unique origins, unsafe due to unhealthy higher sequence ID, stuck report sampling, non-Ratis pass-through, read-only no command, and chain continuation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/QuasiClosedContainerHandler.java -->
