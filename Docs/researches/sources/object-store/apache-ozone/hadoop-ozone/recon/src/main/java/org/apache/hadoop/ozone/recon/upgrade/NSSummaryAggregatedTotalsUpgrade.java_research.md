# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/NSSummaryAggregatedTotalsUpgrade.java

Purpose: `NSSummaryAggregatedTotalsUpgrade` is an upgrade action that triggers asynchronous rebuild of the namespace summary tree when aggregated totals are introduced.

Important APIs and types: annotated for `ReconLayoutFeature.NSSUMMARY_AGGREGATED_TOTALS`. `execute(DataSource)` obtains the global Guice injector from `ReconGuiceServletContextListener`, retrieves `ReconTaskController`, and queues a manual reinitialization event.

Control flow and integration: layout finalization invokes this action. The controller's reinitialization path rebuilds tasks against a checkpoint and staged Recon DB. The action logs an error if queueing does not return `SUCCESS`, but does not throw for non-success results.

State and persistence: no direct DB writes through the provided `DataSource`; persistence happens indirectly when reinitialization tasks rebuild Recon state.

Dependencies: global Guice injector, `ReconTaskController`, `ReconTaskReInitializationEvent`.

Risks and test signals: relying on a global injector makes this action startup-order sensitive. Non-success queue result only logs, so finalization may advance even if rebuild is deferred. Tests should cover missing injector, controller lookup, success queueing, and non-success logging behavior.
