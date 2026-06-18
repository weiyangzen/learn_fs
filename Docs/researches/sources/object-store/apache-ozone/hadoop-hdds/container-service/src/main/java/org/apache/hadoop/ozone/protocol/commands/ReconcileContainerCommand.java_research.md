# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/ReconcileContainerCommand.java

Purpose: SCM command instructing a datanode to reconcile a container replica with peer datanodes.

Important APIs and functions: the constructor uses container ID as command ID so only one reconciliation for a container should be active. `getType` returns `reconcileContainerCommand`. `getProto` serializes container ID and peer datanode protos. `getFromProtobuf` restores peers into a set, or an empty set if none are present. Accessors expose peer datanodes and container ID. Equality and hash code compare only container ID.

Control flow and state: peer set is stored directly and can be mutable depending on the caller. Deduplication ignores peer changes for the same container.

Dependencies and integration: used with `ContainerController.reconcileContainer` and datanode/SCM command transport.

Risks and test signals: equality ignoring peers is intentional for one-at-a-time reconciliation but can suppress updated peer sets. Tests should cover proto round trip, empty peer list, equality semantics, command ID/container ID identity, and peer datanode conversion.
