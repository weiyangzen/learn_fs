## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/ReconstructECContainersCommand.java

Purpose: `ReconstructECContainersCommand` is the SCM-to-datanode command used to request erasure-coded container reconstruction. It carries the container ID, source datanodes with replica indexes, target datanodes, missing EC indexes as a `ByteString`, and an `ECReplicationConfig`.

Important APIs and types: the class extends `SCMCommand<ReconstructECContainersCommandProto>`, reports type `reconstructECContainersCommand`, serializes through `getProto()`, and deserializes through `getFromProtobuf()`. The nested `DatanodeDetailsAndReplicaIndex` type serializes `DatanodeDetails` plus an EC replica index and implements value equality.

Control flow and state: constructors either allocate a command id through `HddsIdFactory.getLongId()` or accept an id during protobuf reconstruction. The main validation enforces `targetDatanodes.size() == missingContainerIndexes.size()`, tying each reconstruction target to one missing index byte. `getProto()` copies source and target details into protobuf lists and writes the EC config. Deserialization maps protobuf source and target lists back to Java objects and preserves `cmdId`.

Persistence and integration: the object itself is transient command state; persistence is protobuf transport and any command queues using the base `SCMCommand` id, term, encoded token, and deadline. It integrates with EC reconstruction scheduling, datanode command handlers, `DatanodeDetails`, and `StorageContainerDatanodeProtocolProtos`.

Risks and test signals: the command stores input lists directly, so callers can mutate lists after construction unless they provide immutable lists. The target/index cardinality check is important because a malformed command cannot be interpreted safely. `toString()` logs encoded tokens and all participating nodes; that is useful for diagnosis but sensitive if tokens are meaningful. No direct tests are in this subset, so coverage likely comes from command serialization tests elsewhere.
