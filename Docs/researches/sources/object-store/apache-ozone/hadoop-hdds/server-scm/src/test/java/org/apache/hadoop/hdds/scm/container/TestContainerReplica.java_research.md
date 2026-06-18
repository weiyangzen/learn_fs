# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerReplica.java

## Purpose

This small test verifies that `ContainerReplica.toBuilder()` preserves all significant fields when rebuilding a replica object.

## Important APIs, Types, and Functions

- `ContainerReplica.newBuilder` sets bytes used, container ID, state, key count, origin node ID, sequence ID, replica index, and datanode details.
- `ContainerReplica.toBuilder().build()` creates the copy under test.
- `assertEquals` compares the original and copy, and also compares `toString`.

## Control Flow and State Behavior

The test builds one randomized closed `ContainerReplica`, calls `toBuilder`, rebuilds it, and verifies equality. It also compares string representations because a comment notes `equals` is incomplete, making the string check a guard for fields not covered by equality.

## State and Persistence

No persistence exists. Random field values are generated in memory using `ThreadLocalRandom`, `DatanodeID.randomID`, and `MockDatanodeDetails`.

## Dependencies and Integration Points

The file depends on `ContainerReplica`, `ContainerID`, `DatanodeID`, and mock datanode details. It protects builder/copy behavior used by container report processing, replica state mutation, and tests that clone replicas before modifying fields.

## Risks and Test Signals

The main risk is `toBuilder` omitting a field, causing later mutation code to drop metadata silently. Equality plus `toString` comparison provides a compact regression signal.
