# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/DatanodeEntry.java

## Purpose
`DatanodeEntry` is the `NodeStateMap` value object pairing a `DatanodeInfo` with the set of container IDs currently associated with that datanode.

## Important APIs, Types, And Functions
It stores `DatanodeInfo info` and a `TreeSet<ContainerID> containers`. Methods expose `getInfo`, `getContainerCount`, `copyContainers`, `add`, `remove`, and test-only `setContainersForTesting`.

## Control Flow
The class only mutates its set when called by `NodeStateMap`, which provides external locking. `copyContainers` returns a new `TreeSet`, preserving sorted container order and avoiding direct set mutation by callers.

## State And Persistence Behavior
State is in-memory only. The container set is not persisted here; SCM rebuilds or updates it via reports and container event handling around the broader node state manager.

## Dependencies And Integration Points
It depends on `DatanodeInfo` and `ContainerID` and is package-private for construction by `NodeStateMap`. It is not a public node-management API.

## Risks And Edge Cases
The internal set is not synchronized by itself, so it relies on `NodeStateMap` lock discipline. `updateNode` in `NodeStateMap` replaces the entire entry and therefore can discard existing container membership if used without migration.

## Test Signals
Tests should validate sorted copy behavior, add/remove idempotence, and preservation or intentional replacement of container membership during node updates.
