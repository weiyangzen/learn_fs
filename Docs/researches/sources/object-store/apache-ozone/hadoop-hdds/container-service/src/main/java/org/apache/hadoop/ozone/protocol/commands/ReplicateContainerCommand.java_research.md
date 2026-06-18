## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/ReplicateContainerCommand.java

Purpose: `ReplicateContainerCommand` tells a datanode to replicate a container, either from a list of source datanodes or to a target datanode depending on how the command is constructed.

Important APIs and types: the class is final and extends `SCMCommand<ReplicateContainerCommandProto>`. Static factories are `fromSources`, `toTarget`, and `forTest`. It exposes container ID, sources, target, replica index, priority, protobuf conversion, and `contributesToQueueSize()`.

Control flow and state: normal commands are created through private constructors without an explicit id, while protobuf reconstruction preserves `cmdId`. `getProto()` writes container ID, all source nodes, replica index, optional target, and priority. `getFromProtobuf()` reconstructs optional target, optional replica index, and optional priority. Queue accounting returns false for non-normal priorities.

Persistence and integration: command state is serialized through `ReplicateContainerCommandProto` and participates in SCM command queue throttling through `contributesToQueueSize`. It integrates with datanode replication tasks, container balancer or replication manager paths, and `DatanodeDetails` protobuf conversion.

Risks and test signals: source and target modes are not mutually enforced by the constructor, so invalid combinations rely on factory discipline and downstream handling. Source list mutability is exposed. Priority affects queue size and can change scheduling behavior. Direct tests are not in this subset; `TestReconcileContainerTask` gives comparable replication-task status and equality signals for a neighboring command family.
