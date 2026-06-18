## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/protocol/commands/TestReconstructionECContainersCommands.java

Purpose: Tests `ReconstructECContainersCommand` validation and protobuf round-trip behavior for erasure-coded container reconstruction commands.

Important APIs/types/functions: `ReconstructECContainersCommand`, nested `DatanodeDetailsAndReplicaIndex`, `ECReplicationConfig`, `getProto`, `getFromProtobuf`, `DatanodeDetails.getFromProtoBuf`, and `UnsafeByteOperations.unsafeWrap`.

Control flow: One test constructs mismatched missing-index and target-datanode counts and expects `IllegalArgumentException`. Round-trip test builds five source datanodes with replica indexes, two targets, missing indexes `{1,2}`, and EC 3-2 config; asserts `toString` includes missing indexes, proto fields match originals, and reconstructed command equals original semantic fields.

State and persistence behavior: Pure in-memory command/protobuf testing.

Dependencies and integration points: Supports SCM-to-datanode EC reconstruction command protocol consumed by EC reconstruction tasks/supervisor.

Risks and test signals: Strong serialization compatibility signal. It does not verify command execution, only construction and conversion.
