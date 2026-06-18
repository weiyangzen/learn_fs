# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/CreatePipelineCommand.java

Purpose: SCM command asking datanodes to create a pipeline with specified replication type, factor, members, and priority list.

Important APIs and functions: constructors build a command with default Ratis priority list when datanode count matches `XceiverServerRatis.getDefaultPriorityList`, with all low priorities otherwise, or with a suggested leader assigned high priority. The protobuf constructor restores command ID and priority list. `getProto` serializes pipeline ID, type, factor, datanodes, and priorities. Accessors expose pipeline, node list, priority list, replication type, and factor.

Control flow and state: priority list is initialized at construction and then exposed directly. `toString` includes inherited command metadata and all pipeline creation fields.

Dependencies and integration: consumed by datanode xceiver server setup and sent from SCM during pipeline allocation.

Risks and test signals: priority list length must match datanode list length. Tests should cover default priority selection, suggested leader high priority, protobuf round trip, datanode conversion, non-standard replication factors, and list mutability exposure.
