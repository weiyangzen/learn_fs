# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/ContainerReportQueue.java

Purpose: `ContainerReportQueue` is a specialized `BlockingQueue` for SCM full and incremental container reports. It preserves fair per-datanode ordering while reducing redundant full container reports and optionally merging incremental reports in subclasses.

Important APIs and types: It implements `BlockingQueue<ContainerReport>` and `FixedThreadPoolWithAffinityExecutor.IQueueMetrics`. The queue stores datanode UUIDs in `orderingQueue` and per-datanode report lists in `dataMap`. Public queue methods include `add`, `offer`, `put`, `take`, `poll`, `peek`, `element`, `size`, `remainingCapacity`, `clear`, and `getAndResetDropCount`.

Control flow: Adding an FCR removes the latest queued FCR for the same datanode if present, decrements capacity, increments `droppedCount`, then enqueues the new report. Adding an ICR tries `mergeIcr`; if not merged, it appends and records ordering. Removal takes the next UUID from `orderingQueue` and removes the first report from that datanode's list.

State and persistence behavior: State is in-memory only: queue capacity, UUID ordering, report lists, and dropped FCR counter. There is no persistence.

Dependencies and integration points: It consumes `SCMDatanodeHeartbeatDispatcher.ContainerReport` types and is intended for SCM event executor queues that process full and incremental reports. Drop counts are exposed for queue metrics by event type name.

Risks: Several `BlockingQueue` operations are unsupported and throw. `isEmpty()` checks only `orderingQueue` without synchronizing on `dataMap`. `put` and timed `offer` sleep-loop rather than using condition variables. Capacity and ordering must stay balanced; bugs in report replacement can strand UUID entries or report lists.

Test signals: Tests should cover FCR replacement and drop counts, ICR append order, subclass ICR merge behavior, capacity limits, blocking/timed offer behavior, per-datanode fair order, clear, and unsupported operation exceptions.
