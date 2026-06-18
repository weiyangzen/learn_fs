<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerEntry.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerEntry.java

## Purpose

`ContainerEntry` stores a `ContainerInfo` and its current replica set for `ContainerStateMap`. It keeps replicas keyed by datanode ID while exposing immutable snapshot sets to readers.

## Important APIs, Types, and Functions

Public methods are `getInfo`, `getReplicas`, `put`, and `removeReplica`. The private `copyAndUpdate` updates the mutable map and rebuilds the immutable exposed replica set.

## Control Flow

Adding or removing a replica mutates the `TreeMap<DatanodeID, ContainerReplica>`, then copies map values into a new `HashSet` and publishes it as an unmodifiable set. `put` returns the replaced replica, and `removeReplica` returns the removed replica.

## State and Persistence Behavior

State is in-memory container info plus a replica map and immutable set snapshot. There is no persistence. Thread safety relies on owning `ContainerStateMap` usage.

## Dependencies and Integration Points

It integrates with `ContainerStateMap` replica update/remove paths. Datanode ID ordering in the `TreeMap` gives deterministic map storage, while set exposure prevents external mutation.

## Risks and Edge Cases

Every replica update copies the full replica map to a set, which is fine for small replication factors but worth noting. Equality semantics of `ContainerReplica` affect set uniqueness after values are copied.

## Test Signals

Tests should assert immutable set exposure, replacement return value on same datanode, removal return value, info identity preservation, and snapshot changes after updates.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerEntry.java -->
