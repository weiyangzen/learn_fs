<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ECReplicationCheckHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ECReplicationCheckHandler.java

## Purpose

`ECReplicationCheckHandler` classifies EC containers as healthy, under-replicated, over-replicated, missing, unhealthy, or combinations involving offline indexes. It enqueues repair work when pending ops are insufficient.

## Important APIs, Types, and Functions

Important methods are `handle` and `checkHealth`. It constructs `ECContainerReplicaCount`, reads `ECReplicationConfig`, emits `UnderReplicatedHealthResult` or `OverReplicatedHealthResult`, and samples `ContainerHealthState` variants including `MISSING_UNDER_REPLICATED`, `UNHEALTHY_UNDER_REPLICATED`, `MISSING`, `UNHEALTHY`, `UNDER_REPLICATED`, and `OVER_REPLICATED`.

## Control Flow

The handler ignores non-EC containers. `checkHealth` first tests sufficient replication without pending ops, computes missing indexes and remaining redundancy, distinguishes true missing from out-of-service-only cases, sets offline-index and missing flags, and returns under health. It then checks over-replication. `handle` maps the result to report states and queues only if pending operations do not already repair the relevant deficit.

## State and Persistence Behavior

No direct persistence occurs. State changes are report samples and queue entries. The calculation includes pending ops and maintenance redundancy from `ContainerCheckRequest`.

## Dependencies and Integration Points

It integrates with `ECContainerReplicaCount`, EC replication config, decommission/maintenance monitors that rely on offline-index state, ReplicationQueue, and later EC under/over replication handlers.

## Risks and Edge Cases

EC containers can be both unrecoverable and blocked by offline indexes; this handler intentionally reports both through combined states. Pending-op checks differ for offline indexes versus missing indexes. Incorrect `remainingRedundancy` can affect reconstruction urgency.

## Test Signals

Tests should cover missing indexes, unrecoverable EC sets, offline-only under replication, pending-add fixes, over-replicated indexes, maintenance redundancy, missing versus unhealthy classification, and queue suppression when pending ops are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ECReplicationCheckHandler.java -->
