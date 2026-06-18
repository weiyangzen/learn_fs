<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerReportHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerReportHandler.java

## Purpose
Processes full container reports from datanodes. It reconciles the datanode-to-container map, updates SCM's container replica map and stats, handles unknown reported containers, removes replicas missing from the full report, and emits registration-report events.

## Important APIs, Types, And Functions
`ContainerReportHandler` extends `AbstractContainerReportHandler` and implements `EventHandler<ContainerReportFromDatanode>`. The constructor reads `ScmConfig.getUnknownContainerAction()` into `UnknownContainerAction.WARN` or `DELETE`. `onMessage` performs full reconciliation. `processSingleReplica` handles known or unknown replicas. `processMissingReplicas` removes containers missing from the datanode report from both `NodeManager` and `ContainerManager`. `UnknownContainerAction.parse` defaults unknown config strings to WARN.

## Control Flow
The handler resolves the canonical datanode object from `NodeManager`, synchronizes on it to prevent concurrent full and incremental processing, snapshots expected containers from `NodeManager`, then iterates reported replicas. Each known replica reuses the `ContainerID` from `ContainerInfo`, removes it from the expected set, adds new node-manager mappings, clears pending allocation for first confirmation, validates via `ContainerReportValidator`, and delegates to shared replica processing. After the loop, remaining expected IDs are treated as missing and removed. Successful processing increments full-report metrics and registration reports fire a separate registration event.

## State And Persistence
Node-to-container membership is updated in `NodeManager`; container replica state is updated or removed in `ContainerManager`; container lifecycle and stats may persist through shared handler paths. Unknown containers may result in a delete command instead of SCM metadata updates depending on configuration.

## Dependencies And Integration Points
Integrates datanode heartbeat reports, `NodeManager`, `ContainerManager`, `DatanodeInfo` pending allocation tracking, `ContainerReportValidator`, SCM events, registration report handling, and the shared abstract report state machine.

## Risks And Test Signals
Correctness depends on `NodeManager.getContainers` snapshot semantics: modifying the returned set must not corrupt iteration expectations. Full and incremental report serialization is per datanode object, so canonical datanode resolution is critical. Tests should cover unknown WARN and DELETE modes, missing replica removal, new replica addition, pending allocation clearing, validator skip behavior, registration events, NodeNotFound handling, and full-report metrics success/failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerReportHandler.java -->
