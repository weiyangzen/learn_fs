<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerAttribute.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerAttribute.java

## Purpose

`ContainerAttribute` is a generic enum-keyed index from container attributes, such as lifecycle state or replication type, to sorted maps of `ContainerID` to `ContainerInfo`. It supports fast in-memory selection by attribute for `ContainerStateMap`.

## Important APIs, Types, and Functions

Important methods are `addNonExisting`, `clearSet`, `remove`, `removeExisting`, `getCollection`, `tailMap`, `count`, and `update`. It stores an immutable enum map whose values are mutable `TreeMap`s.

## Control Flow

Construction creates one empty `TreeMap` for each enum constant. Add/remove operations assert consistency. `update` removes a container ID from its current enum bucket and adds the same `ContainerInfo` to the new bucket, throwing `SCMException` if the old mapping is missing.

## State and Persistence Behavior

State is in-memory only. The class is explicitly not thread-safe and relies on `ContainerStateMap` external locking/serialization. Sorted maps preserve container-ID ordering for pagination.

## Dependencies and Integration Points

It is used by `ContainerStateMap` to index lifecycle states and replication types. It depends on `ContainerID`, `ContainerInfo`, Guava immutable enum maps, Ratis preconditions, and SCM exceptions.

## Risks and Edge Cases

Passing an enum value not in the attribute class throws. Updating from a missing current bucket throws `FAILED_TO_CHANGE_CONTAINER_STATE`. `getCollection` returns a copy, while `tailMap` exposes the underlying sorted map view.

## Test Signals

Tests should cover all enum buckets created, add duplicate assertion, remove existing identity assertion, update success and missing-current failure, sorted tail-map behavior, count accuracy, and external synchronization assumptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/states/ContainerAttribute.java -->
