## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/SCMCommand.java

Purpose: `SCMCommand` is the abstract base for commands SCM sends to datanodes. It standardizes command identity, command type, protobuf conversion, leader term, encoded token, optional deadline, and queue accounting.

Important APIs and types: the generic type parameter is a protobuf `Message`. Subclasses implement `getType()` and `getProto()`. The class implements `IdentifiableEventPayload`, so `getId()` is the event identity. `hasExpired(currentEpochMs)` enforces optional deadline semantics.

Control flow and state: constructors either allocate a long id through `HddsIdFactory.getLongId()` or accept a provided id for protobuf reconstruction. Term defaults to zero until set. Encoded token defaults to empty string. Deadline defaults to zero, which means no deadline. `hasExpired()` returns true only when a positive deadline is earlier than the checked time. `contributesToQueueSize()` defaults true and can be overridden, as `ReplicateContainerCommand` does for priority.

Persistence and integration: this base state is serialized by each concrete command's protobuf and used by SCM event queues, heartbeat command delivery, and datanode status reporting. It has no direct disk persistence.

Risks and test signals: subclasses must remember to serialize inherited metadata that matters; the base class cannot enforce that. Mutable token, term, and deadline are not synchronized. Deadline enforcement is caller-owned, so omission in command handlers can make deadlines inert. This subset contains multiple subclasses showing both normal id preservation and intentional exceptions.
