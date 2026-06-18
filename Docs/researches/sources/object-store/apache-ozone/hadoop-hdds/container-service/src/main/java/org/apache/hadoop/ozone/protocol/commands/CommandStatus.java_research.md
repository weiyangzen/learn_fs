# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/CommandStatus.java

Purpose: represents datanode execution status for an SCM command.

Important APIs and functions: fields store command type, command ID, protobuf status enum, and optional message. `markAsExecuted` and `markAsFailed` update status. `getFromProtoBuf` builds a new status from protobuf. `getProtoBufMessage` serializes fields, including message only when non-null. Nested `CommandStatusBuilder` provides fluent construction.

Control flow and state: status is mutable after construction, while type/cmdId/message are only changed through builder before build. The `getFromProtoBuf` method is an instance method even though it behaves like a converter.

Dependencies and integration: used in datanode heartbeat command status reporting, with `DeleteBlockCommandStatus` extending it for block deletion acknowledgements.

Risks and test signals: null required fields can produce invalid protobuf builders. Tests should cover executed/failed transitions, message omission, protobuf round trip, builder defaults, and subclass override behavior.
