# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/reconciliation/ReconcileContainerEventHandler.java

Purpose: event handler that starts container reconciliation by sending reconcile commands to all datanodes holding an eligible container replica.

Important APIs: constructor and `onMessage(ContainerID, EventPublisher)`.

Control flow and state: first checks `SCMContext.isLeader`; then uses `ReconciliationEligibilityHandler`. If eligible, it gathers all replica datanodes, and for each replica fires a `DATANODE_COMMAND` containing `ReconcileContainerCommand(containerId, otherReplicas)` with the current leader term. It catches container-not-found and not-leader cases.

Dependencies and integration: depends on `ContainerManager`, `SCMContext`, event bus, `CommandForDatanode`, and `ReconcileContainerCommand`. Tested by `TestReconcileContainerEventHandler`.

Risks: TODO notes peer/target nodes are not restricted by node status. The replica set can change between eligibility and command creation. Tests should cover leader false, not-leader exception, no replicas, ineligible state/type, and command peer sets for each target.
