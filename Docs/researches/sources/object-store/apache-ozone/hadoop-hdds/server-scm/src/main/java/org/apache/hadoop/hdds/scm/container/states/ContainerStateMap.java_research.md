<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerStateMap.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerStateMap.java

## Purpose

`ContainerStateMap` is SCM's in-memory index of containers and their replicas. It maintains the primary container-ID map plus secondary indexes by lifecycle state and replication type for allocation, listing, and replication scans.

## Important APIs, Types, and Functions

Important methods include `addContainer`, `contains`, `removeContainer`, `getContainerInfo`, `getContainerReplicas`, `updateContainerReplica`, `removeContainerReplica`, `updateState`, `getContainerIDs`, `getContainerInfos`, and `getContainerCount`. The nested `ContainerMap` stores `ContainerID -> ContainerEntry` in a `ConcurrentSkipListMap`.

## Control Flow

Adding a container inserts into the primary map if absent, then adds to lifecycle and type indexes. Removing a container removes from all indexes. Replica updates delegate to the entry for the target container. State updates move the container ID between lifecycle buckets and then mutate the `ContainerInfo` state field. Listing uses sorted tail maps for pagination.

## State and Persistence Behavior

All state is in-memory and reconstructed from persistent SCM metadata elsewhere. The class declares itself not thread-safe despite the concurrent primary map; consistency across primary and secondary indexes depends on external synchronization.

## Dependencies and Integration Points

It integrates with SCM container manager/state manager, replication manager scans, allocation queries, report processing, and container lifecycle state transitions. It depends on `ContainerAttribute`, `ContainerEntry`, protobuf lifecycle/replication enums, `ContainerReplica`, and `SCMException`.

## Risks and Edge Cases

Duplicate add is idempotent and does not update existing info. Updating state for a missing container silently returns, while missing secondary-index state raises from `ContainerAttribute`. `getContainerReplicas` returns null for missing containers, not an empty set.

## Test Signals

Tests should cover add/remove index consistency, idempotent duplicate add, replica add/replace/remove, sorted pagination by ID, state update moving counts and mutating info, missing-container behavior, replication type listing, and external locking assumptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerStateMap.java -->
