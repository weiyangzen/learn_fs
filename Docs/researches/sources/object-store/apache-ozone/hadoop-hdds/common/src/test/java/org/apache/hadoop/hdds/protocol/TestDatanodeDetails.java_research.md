# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/protocol/TestDatanodeDetails.java

## Purpose
`TestDatanodeDetails` verifies datanode protocol serialization around port compatibility and current-version fallback behavior.

## APIs and dependencies
The tests use `DatanodeDetails`, `MockDatanodeDetails`, `DatanodeDetails.Port`, port name sets `ALL_PORTS`, `V0_PORTS`, and `IO_PORTS`, client versions `DEFAULT_VERSION` and `VERSION_HANDLES_UNKNOWN_DN_PORTS`, `DatanodeVersion`, protobuf `HddsProtos.DatanodeDetailsProto`, AssertJ, Guava `ImmutableSet`, and JUnit.

## Control flow and state behavior
`protoIncludesNewPortsOnlyForV1` serializes a mock datanode for an older client version and expects only V0 ports, then serializes for the client version that handles unknown datanode ports and expects all ports. `testRequiredPortsProto` serializes only requested standalone/Ratis ports, then serializes IO ports and checks exact inclusion. `testNewBuilderCurrentVersion` clears the current version from a proto to simulate Ozone 1.4.0 and earlier, then verifies builder fallback to `SEPARATE_RATIS_PORTS_AVAILABLE`; when the field is present, it expects `DatanodeVersion.CURRENT`.

## Integration points
The tests protect protobuf compatibility between clients and datanodes across version upgrades. They also validate selective port exposure used by callers that need only specific service endpoints.

## Risks and test signals
The key risks are exposing unknown ports to old clients, dropping required ports for newer clients, or misinterpreting missing current-version fields from older serialized data. These tests should be updated when protocol version gates or port-name compatibility rules change.
