# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerInfo.java

## Purpose
Tests `ContainerInfo` identity, protobuf conversion, replication config handling, timestamps, pipeline IDs, and state restoration behavior.

## Important APIs, types, and functions
- Uses `ContainerInfo`, `ContainerID`, `PipelineID`, `RatisReplicationConfig`, `ECReplicationConfig`, and `HddsProtos` protobufs.
- Test cases cover hash behavior by container ID, Ratis and EC protobuf round trips, and restoration of lifecycle state.
- Uses `TestClock` and `ThreadLocalRandom` for deterministic time advancement and random IDs.

## Control flow
Builders create container metadata with owner, state, replication config, pipeline, and timestamps. Tests serialize to protobuf and reconstruct, then compare field preservation. Restore-state tests move container lifecycle data through persisted values.

## State and persistence behavior
No actual database is used, but protobuf round trips model persisted SCM container metadata. The tests pay attention to creation/modification timestamps and lifecycle state fields.

## Dependencies and integration points
`ContainerInfo` is central SCM metadata consumed by replication, placement, and pipeline code. The protobuf contract integrates with persisted SCM state and wire messages.

## Risks and test signals
Losing replication type/factor, EC config, pipeline ID, or timestamps during serialization can corrupt SCM metadata. The tests signal compatibility for both Ratis and EC containers.
