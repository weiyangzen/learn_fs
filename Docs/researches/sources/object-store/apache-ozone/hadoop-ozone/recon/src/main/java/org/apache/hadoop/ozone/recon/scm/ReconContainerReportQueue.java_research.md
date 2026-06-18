## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconContainerReportQueue.java

Purpose: `ReconContainerReportQueue` customizes SCM's `ContainerReportQueue` so Recon can coalesce adjacent incremental container reports in the same queue slot.

Important APIs and types: the constructor delegates queue size to the parent. `mergeIcr(ContainerReport, List<ContainerReport>)` checks the last queued report type and calls `mergeReport` when the last item is an ICR.

Control flow: enqueue logic in the parent calls `mergeIcr`. Recon merges a new ICR only with the most recent queued ICR, preventing repeated ICR events from creating unnecessary queue pressure while avoiding merges across other report types.

State and persistence: no durable state. The only state is the in-memory queue owned by the parent class and the mutable `ContainerReport` payload created by `mergeReport`.

Dependencies and integration points: `ReconUtils.initContainerReportQueue` is used by `ReconStorageContainerManagerFacade` to create report queues for the fixed-affinity executor handling FCR/ICR events.

Risks and edge cases: merging only the last ICR is simple but assumes parent queue ordering remains meaningful. If `mergeReport` grows very large, a burst from one datanode can still create a large single payload. FCRs are not merged, preserving full-report semantics.

Test signals: no direct class test was found. Tests should cover adjacent ICR merge, no merge when the previous item is an FCR, and preservation of report type ordering.
