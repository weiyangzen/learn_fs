<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/HealthCheck.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/HealthCheck.java

## Purpose

`HealthCheck` defines the contract for ReplicationManager container health check handlers and their chain-of-responsibility execution.

## Important APIs, Types, and Functions

The interface declares `handle`, `handleChain`, and `addNext`, all using `ContainerCheckRequest`.

## Control Flow

Concrete handlers implement direct classification and side effects in `handle`. `handleChain` is implemented by `AbstractCheck` to call handlers in sequence until one returns handled or the chain ends. `addNext` wires the chain.

## State and Persistence Behavior

The interface owns no state. Implementations may sample reports, enqueue health results, send commands, or update container lifecycle state.

## Dependencies and Integration Points

It is the common type for all health handlers in `org.apache.hadoop.hdds.scm.container.replication.health`, used during ReplicationManager scans.

## Risks and Edge Cases

Handler return semantics are not simply "did anything": some handlers return `false` after command side effects to allow later checks. Read-only behavior is implementation-specific but expected for report-only scans.

## Test Signals

Tests should focus on concrete chain ordering and verify that each handler's return value either stops or continues processing as intended.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/HealthCheck.java -->
