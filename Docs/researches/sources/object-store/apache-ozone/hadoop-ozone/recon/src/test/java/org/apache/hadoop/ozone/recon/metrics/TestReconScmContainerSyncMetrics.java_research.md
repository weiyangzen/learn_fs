# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/metrics/TestReconScmContainerSyncMetrics.java

Purpose: This test verifies that `ReconScmContainerSyncMetrics` emits gauges only for container lifecycle states reconciled by the SCM container sync path: `OPEN`, `QUASI_CLOSED`, `CLOSED`, and `DELETED`. It also checks global sync status and duration gauges.

Important APIs/types/functions: The suite uses `ReconScmContainerSyncMetrics.create`, `unRegister`, `setContainerSyncDurationMs`, `setContainerCountDrift`, `setScmContainerSyncStatus`, `setScmContainerSyncDurationMs`, `MetricsAsserts.getMetrics`, `getIntGauge`, `getLongGauge`, `MetricsRecordBuilder`, and lifecycle constants `OPEN`, `QUASI_CLOSED`, `CLOSED`, `DELETED`, `CLOSING`, and `DELETING`.

Control flow: Setup registers a metrics instance and teardown unregisters it. The test sets durations and drifts for reconciled states and also sets values for non-reconciled `CLOSING`/`DELETING`. It obtains a metrics record builder and asserts present gauges for reconciled states while verifying the builder never received gauges for non-reconciled states.

State and persistence behavior: State is in-memory metrics values. There is no persistence. Unregistration avoids cross-test metrics conflicts.

Dependencies and integration points: These metrics surface Recon SCM container sync status and per-state drift/duration to Hadoop metrics consumers. The test locks down the public metric names such as `openContainerSyncDurationMs`, `quasiClosedContainerCountDrift`, and `scmContainerSyncStatus`.

Risks: The negative `verify(builder, never()).addGauge(...)` checks depend on metric builder mock behavior from `MetricsAsserts`. If new lifecycle states become reconciled, this test must change intentionally. It does not test metric reset behavior across sync cycles.

Test signals: Status gauge equals `SCM_CONTAINER_SYNC_STATUS_SUCCESS`; total sync duration equals 500; open/quasi-closed/closed/deleted durations equal 10/20/30/40; corresponding drift values equal 2/0/-3/4; and no gauges are emitted for closing/deleting duration or drift despite setters being called.
