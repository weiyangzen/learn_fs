# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/CommandForDatanode.java

Purpose: event payload wrapper pairing an `SCMCommand` with its intended datanode destination.

Important APIs and functions: constructors accept either `DatanodeDetails` or `DatanodeID` plus a generic `SCMCommand<T>`. `getDatanodeId` and `getCommand` expose fields. `getId` implements `IdentifiableEventPayload` by returning the command ID.

Control flow and state: immutable wrapper with no side effects.

Dependencies and integration: used in SCM event pipelines where commands are routed to a specific datanode. Generic bound requires protobuf `Message` command payloads.

Risks and test signals: command ID is used as event identity, so duplicate command IDs can collide. Tests should cover construction from details and ID, event ID forwarding, generic command access, and string representation.
