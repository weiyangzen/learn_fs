# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/DeleteContainerCommand.java

Purpose: SCM command telling a datanode to delete a container, optionally forcefully and for a specific replica index.

Important APIs and functions: constructors accept raw container ID or `ContainerID` and force flag. `setReplicaIndex` mutates the replica index, defaulting to zero. `getType` returns `deleteContainerCommand`. `getProto` serializes command ID, container ID, force, and replica index. `getFromProtobuf` restores container ID, force, and optional replica index. Accessors expose container ID, force, and replica index.

Control flow and state: unlike many commands, local `containerId` is separate from inherited command ID. `toString` includes inherited metadata and deletion fields.

Dependencies and integration: consumed by datanode container deletion handlers and SCM replica management.

Risks and test signals: protobuf restoration does not preserve `cmdId` into inherited ID because the constructor does not accept it. Tests should verify whether that is intentional, plus force behavior, replica index optionality, container ID round trip, and command ID semantics.
