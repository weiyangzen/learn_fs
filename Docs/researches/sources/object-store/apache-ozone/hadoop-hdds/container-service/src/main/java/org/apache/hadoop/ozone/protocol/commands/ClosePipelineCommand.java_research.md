# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/ClosePipelineCommand.java

Purpose: SCM command requesting a datanode to close a Ratis pipeline.

Important APIs and functions: constructors create a new command ID or restore one from protobuf. `getType` returns `closePipelineCommand`. `getProto` serializes command ID and pipeline ID. `getFromProtobuf` reconstructs the command. `getPipelineID` exposes the target pipeline.

Control flow and state: state is the immutable pipeline ID plus inherited SCM command metadata. `toString` includes token, term, deadline, and pipeline.

Dependencies and integration: consumed by datanode xceiver/Ratis pipeline management and transported via SCM heartbeat commands.

Risks and test signals: risk is mostly serialization compatibility. Tests should cover proto round trip, null proto rejection, command ID preservation, pipeline ID conversion, and diagnostic string content.
