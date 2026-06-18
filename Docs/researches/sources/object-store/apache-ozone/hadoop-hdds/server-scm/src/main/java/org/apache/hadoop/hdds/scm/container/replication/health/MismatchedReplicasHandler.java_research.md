<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/MismatchedReplicasHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/MismatchedReplicasHandler.java

## Purpose

`MismatchedReplicasHandler` sends close commands for replicas whose state lags the SCM container state, while deliberately allowing later health checks to continue processing under/over/mis-replication.

## Important APIs, Types, and Functions

Main methods are `handle` and private `getTransitionState`. It calls `ReplicationManager.sendCloseContainerReplicaCommand` and examines `LifeCycleState.CLOSED`, `QUASI_CLOSED`, replica states `OPEN`, `CLOSING`, `QUASI_CLOSED`, and replication type.

## Control Flow

Read-only requests pass through. Non-closed/non-quasi-closed containers pass through. For open or closing replicas, Ratis targets quasi-closed and EC/non-Ratis targets closed. For quasi-closed replicas of closed containers, it force closes only when sequence IDs match. The handler always returns `false`.

## State and Persistence Behavior

No direct persistent update occurs. It sends commands whose completion later changes replica reports and container state. It does not mutate the report.

## Dependencies and Integration Points

It integrates with the health chain before replication-count handlers, allowing replica state convergence before over-replication cleanup. It relies on ReplicationManager's close-command API.

## Risks and Edge Cases

Always returning `false` means later handlers can also act on the same scan. Sequence-ID equality protects closed container force-close safety. Read-only scans skip command sending entirely.

## Test Signals

Tests should assert commands for open/closing replicas, force close for matching quasi-closed closed replicas, no command for mismatched sequence IDs, no mutation in read-only mode, non-relevant states pass through, and chain continuation after side effects.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/MismatchedReplicasHandler.java -->
