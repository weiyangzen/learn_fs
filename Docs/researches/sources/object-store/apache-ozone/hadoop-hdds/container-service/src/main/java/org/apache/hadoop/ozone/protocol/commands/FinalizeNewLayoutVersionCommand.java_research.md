# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/FinalizeNewLayoutVersionCommand.java

Purpose: SCM command asking a datanode to finalize or process a new layout version.

Important APIs and functions: constructors set the finalize flag, `LayoutVersionProto`, and optionally command ID. `getType` returns `finalizeNewLayoutVersionCommand`. `getProto` serializes finalize flag, command ID, and datanode layout version. `getFromProtobuf` restores all fields. `toString` includes inherited command metadata plus finalize flag and layout info.

Control flow and state: local state is the boolean finalize flag and layout proto. There are no accessors in this file beyond protobuf/toString, so consumers likely use the proto form or inherited command handling.

Dependencies and integration: used during SCM-driven datanode upgrade finalization, tying into `DataNodeUpgradeFinalizer` and layout-version reporting.

Risks and test signals: command compatibility depends on correct layout proto fields. Tests should cover protobuf round trip, command ID preservation, finalize true/false behavior, null layout handling, and datanode upgrade command execution.
