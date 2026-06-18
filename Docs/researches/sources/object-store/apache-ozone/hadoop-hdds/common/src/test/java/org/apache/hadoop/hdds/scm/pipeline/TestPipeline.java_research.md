# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipeline.java

## Purpose
Tests `Pipeline` protobuf conversion, EC replica indexes, health semantics, builder copy behavior, replacement identity, and read-node targeting.

## Important APIs, types, and functions
- Uses `Pipeline`, `MockPipeline`, `PipelineID`, `DatanodeDetails`, `HddsProtos`, and replication config classes.
- Test cases include `protoIncludesNewPortsOnlyForV1`, `getProtobufMessageEC`, `testReplicaIndexesSerialisedCorrectly`, `testECPipelineIsAlwaysHealthy`, `testBuilderCopiesAllFieldsFromOtherPipeline`, `idChangedIfNodesReplaced`, `testCopyForReadFromNode`, and rejection of unknown read nodes.

## Control flow
The tests create pipelines, serialize to protobuf with specific client versions, inspect node/port and EC fields, copy builders, replace nodes, and build read-specific pipeline variants.

## State and persistence behavior
Pipelines are in-memory metadata objects. Protobuf conversion models wire/persisted state, especially client-version-sensitive datanode ports and EC replica indexes.

## Dependencies and integration points
Pipeline metadata is used by clients, SCM, and datanodes. Compatibility with protobuf client versions and EC topology is central.

## Risks and test signals
Risks include losing replica indexes, exposing incompatible ports to older clients, reusing IDs after node replacement, or accepting invalid read targets. The tests provide contract signals across these behaviors.
