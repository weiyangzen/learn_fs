# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/ContainerWithPipeline.java

## Purpose
Combines a `ContainerInfo` and its `Pipeline` for allocation/list responses, with protobuf conversion and ordering by container recency comparator.

## Important APIs, Types, And Functions
`fromProtobuf`, `getProtobuf(int clientVersion)`, getters, `equals`, `hashCode`, `compare`, and `compareTo` are key. Serialization uses `Pipeline.getProtobufMessage(clientVersion, Name.IO_PORTS)`.

## Control Flow
SCM APIs return this when clients need both metadata and connection pipeline. Protobuf conversion reconstructs both parts from HddsProtos.

## State And Persistence
The wrapper is immutable and transient. It serializes for RPC/API transport but does not persist authoritative state.

## Dependencies And Integration Points
Depends on `ContainerInfo`, `Pipeline`, HddsProtos, and datanode port-name selection. Integrated by allocate/list container APIs and client write paths.

## Risks And Test Signals
Comparison delegates to `ContainerInfo.compareTo`, not ID order. Tests should cover protobuf round trip with client versions, equality/hash, and sorted allocation results.
