<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/IncrementalContainerReportHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/IncrementalContainerReportHandler.java

## Purpose
Processes incremental container reports from datanodes. It updates the datanode's container membership and the corresponding SCM replica/container state for only the reported changes.

## Important APIs, Types, And Functions
`IncrementalContainerReportHandler` extends `AbstractContainerReportHandler` and implements `EventHandler<IncrementalContainerReportFromDatanode>`. `getDatanodeDetails` resolves the canonical datanode from `NodeManager`. `processICR` synchronizes per datanode, updates `NodeManager` membership, validates replicas, delegates to `processContainerReplica`, clears pending allocations, and notifies report metrics.

## Control Flow
`onMessage` resolves the datanode and returns if unknown. `processICR` locks on the datanode to serialize with full reports, then loops through reported replica protos. In a `finally` block around container lookup, it removes node-manager membership for DELETED replicas and adds it for all others. Known containers are validated and processed. Exceptions are logged by category, including not-leader `SCMException`, and success is true if at least one replica is processed through the main try path.

## State And Persistence
Incremental reports update `NodeManager` membership, in-memory replica maps, pending allocation tracking, and possibly persistent container lifecycle/stats through shared abstract processing. It does not reconcile missing replicas; full reports own that path.

## Dependencies And Integration Points
Depends on heartbeat dispatcher ICR payloads, `NodeManager`, `ContainerManager`, `ContainerReportValidator`, `DatanodeInfo` pending allocation tracking, `SCMContext`, and shared report processing. It is the frequent lightweight update path complementing full reports.

## Risks And Test Signals
The membership update happens in a `finally` after container lookup, so unknown containers can still affect node-manager state based on replica state. Success metrics are coarse and may mark success after partial processing. Tests should cover DELETED membership removal, add membership for non-deleted replicas, validator failures, unknown container logging, SCM_NOT_LEADER handling, pending allocation clearing, serialization with FCR, and partial failure metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/IncrementalContainerReportHandler.java -->
