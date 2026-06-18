# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/IEventInfo.java

Purpose: `IEventInfo` is an optional payload-side metadata interface for events that want queue/execution latency tracking.

Important APIs/types/functions: `getCreateTime()` returns the event creation timestamp, expected to be comparable with `Time.monotonicNow()`. `getEventId()` defaults to an empty string and can be overridden for log context.

Control flow: `FixedThreadPoolWithAffinityExecutor.ContainerReportProcessTask` checks whether a queued report implements this interface. If so, it computes queue wait and total execution time against configured thresholds and increments slow-event metrics.

State and persistence: no state in the interface; implementations carry their own timestamp/id fields.

Dependencies/integration: integrated with the fixed-affinity executor and report payload classes. It avoids making all event payloads depend on a concrete base type.

Risks: callers must supply monotonic timestamps, not wall-clock values, or threshold comparisons become invalid. The default event id limits diagnostic value unless implementations override it.

Test signals: fixed-pool executor tests and report-processing integration paths provide indirect coverage of slow queue/execution accounting when payloads implement this contract.
