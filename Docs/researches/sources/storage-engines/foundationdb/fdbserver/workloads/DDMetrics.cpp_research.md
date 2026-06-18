# sources/storage-engines/foundationdb/fdbserver/workloads/DDMetrics.cpp

Purpose: Implements `DDMetrics`, a small workload that measures how long high-priority data distribution relocations remain in flight after a start delay.

Important APIs/types/functions: `DDMetricsWorkload`, `getHighPriorityRelocationsInFlight`, `work`, `getMasterWorker`, `WorkerInterface::eventLogRequest`, `EventLogRequest("MovingData")`, and the `DDDuration` metric.

Control flow: Client 0 waits `beginPoll`, then polls every 2.5 seconds. Each poll contacts the current master worker, requests the latest `MovingData` event fields, parses `UnhealthyRelocations` via `sscanf`, and stops when the value reaches zero.

State and persistence behavior: No database state is changed. Runtime state is only `ddDone`, the elapsed time from polling start to zero high-priority relocations.

Dependencies/integration: It depends on master worker discovery, event-log field names emitted by data distribution, `QuietDatabase`/server info headers, and tester metrics.

Risks: The workload catches and traces errors without failing `check`, so missing event fields or transient master issues may silently leave `ddDone` at zero. The trace event name contains a spelling typo (`Reliocations`), which matters for log searches.

Test signals: `DDMetricsStarting`, `DDMetricsCheck` with `DIF`, `DDMetricsError`, and `DDDuration`.
