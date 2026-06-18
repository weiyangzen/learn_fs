<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/report/ContainerReportValidator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/report/ContainerReportValidator.java

## Purpose

`ContainerReportValidator` validates datanode container-replica reports before SCM accepts them. Current validation is specific to EC replicas: reported replica indexes must be present and within the configured EC required-node range.

## Important APIs, Types, and Functions

The public API is static `validate(ContainerInfo, DatanodeDetails, ContainerReplicaProto)`. Internally it uses a singleton validator map from `ReplicationType` to `ReplicaValidator`, with `ECReplicaValidator` implementing index validation.

## Control Flow

`validate` extracts the container replication config and dispatches by replication type. If no validator exists for the type, validation succeeds. The EC validator rejects non-EC configs defensively and then checks `hasReplicaIndex`, index greater than zero, and index less than or equal to `replicationConfig.getRequiredNodes`.

## State and Persistence Behavior

State is a static immutable validator map. No persistence occurs. Rejection affects report processing upstream rather than modifying metadata here.

## Dependencies and Integration Points

It integrates with datanode full/incremental container report handling, `ContainerInfo`, `ReplicationConfig`, EC replication configuration, and SCM logging.

## Risks and Edge Cases

Ratis and other non-EC types pass by default. Invalid EC reports are logged with container ID, datanode, required node count, and reported index. A null replication type also passes because of the optional dispatch.

## Test Signals

Tests should assert EC index absent/zero/negative/too-large rejection, valid EC indexes acceptance, non-EC pass-through, and defensive rejection when an EC validator receives non-EC config.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/report/ContainerReportValidator.java -->
