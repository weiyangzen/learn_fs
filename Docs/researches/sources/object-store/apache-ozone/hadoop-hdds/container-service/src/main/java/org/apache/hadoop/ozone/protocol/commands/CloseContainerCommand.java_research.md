# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/CloseContainerCommand.java

Purpose: SCM command asking a datanode to close a container in a specific pipeline, optionally forcefully.

Important APIs and functions: constructors store container command ID, `PipelineID`, and force flag. `getType` returns `closeContainerCommand`. `getProto` serializes container ID, command ID, pipeline ID, and force. `getFromProtobuf` reconstructs the command. Accessors expose container ID, pipeline ID, and force. `equals` and `hashCode` compare container, pipeline, and force.

Control flow and state: immutable except inherited SCM command fields and the local force flag set at construction. `toString` includes encoded token, term, deadline, container, pipeline, and force for diagnostics.

Dependencies and integration: sent from SCM to datanodes through heartbeat command responses and handled by datanode pipeline/container logic.

Risks and test signals: protobuf conversion uses `cmdId` as the constructor container ID, matching `getProto` where both are set to `getId`. Tests should cover round trip, force flag, equality, token/term/deadline inherited fields, and pipeline ID conversion.
