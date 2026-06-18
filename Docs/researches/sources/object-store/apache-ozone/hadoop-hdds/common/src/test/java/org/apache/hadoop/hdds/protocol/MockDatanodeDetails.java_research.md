# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/protocol/MockDatanodeDetails.java

## Purpose
`MockDatanodeDetails` is a test factory for constructing `DatanodeDetails` instances with random or explicit identities, hostnames, IP addresses, network locations, and ports.

## APIs and dependencies
Public helpers include `randomDatanodeDetails`, `createDatanodeDetails(String hostname, String loc)`, `createDatanodeDetails(DatanodeID id)`, overloads with explicit host/IP/network location, and `randomLocalDatanodeDetails`. It depends on `DatanodeDetails`, `DatanodeID`, `DatanodeDetails.Port.Name.ALL_PORTS`, `HddsProtos.NodeOperationalState`, `ThreadLocalRandom`, and `GenericTestUtils.PortAllocator`.

## Control flow and state behavior
Random constructors generate IPv4-like addresses and random datanode IDs, then delegate to the main builder. The builder sets ID, host name, IP address, network location, persisted operational state `IN_SERVICE`, expiry `0`, and adds every known datanode port with a shared port number. `randomLocalDatanodeDetails` uses a real free local port from the test utility. The class is non-instantiable and throws from its private constructor.

## Integration points
Tests use these factories wherever realistic datanode descriptors are needed for protocol serialization, pipeline placement, node state, and port handling.

## Risks and test signals
Using the same port for all port names is convenient but may hide bugs that depend on distinct ports. Random addresses can make test failures less reproducible. Adding new port names changes `ALL_PORTS` and therefore the constructed test objects automatically.
