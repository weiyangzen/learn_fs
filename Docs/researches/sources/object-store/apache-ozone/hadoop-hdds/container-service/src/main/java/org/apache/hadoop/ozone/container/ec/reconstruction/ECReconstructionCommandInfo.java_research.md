# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/ECReconstructionCommandInfo.java

## Purpose
`ECReconstructionCommandInfo` is an immutable-ish command adapter that extracts the fields needed by datanode EC reconstruction from `ReconstructECContainersCommand`. It converts command source and target lists into sorted maps keyed by replica index.

## Important APIs and Types
The constructor accepts `ReconstructECContainersCommand`. Public getters expose deadline, container ID, EC replication config, and SCM term. Package-private getters expose unmodifiable sorted source and target maps. `toString` formats command type, replication, missing indexes, source nodes, and target nodes for task debug logging.

## Control Flow
Construction copies scalar command fields, then builds `sourceNodeMap` from each `DatanodeDetailsAndReplicaIndex`. It builds `targetNodeMap` by iterating command target datanodes and pairing each target with the corresponding byte from `missingContainerIndexes`. Duplicate replica indexes keep the first entry because the merge function returns `v1`.

## State and Persistence
The object stores command data in memory only. It performs no persistence and does not mutate the source command. It returns unmodifiable map views, which protects callers from modifying its maps through the getters.

## Dependencies and Integration Points
`ECReconstructionCoordinatorTask` owns one instance and uses it to construct an `AbstractReplicationTask` and invoke `ECReconstructionCoordinator.reconstructECContainerGroup`. `ReconstructECContainersCommandHandler` creates tasks from SCM commands. Tests in `TestReplicationSupervisor` build command info instances for task scheduling, duplicate handling, and equality behavior.

## Risks and Test Signals
The main risk is positional coupling between `missingContainerIndexes` and `targetDatanodes`: if their lengths diverge, `byteAt(i)` can fail or targets can be mapped incorrectly. Duplicate indexes are silently collapsed to the first value, which may hide malformed commands. Existing test signals come from reconstruction command handler and replication supervisor tests; stronger unit coverage would validate mismatched target/index lengths and duplicate-index command behavior.
