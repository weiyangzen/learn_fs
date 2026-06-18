# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/metrics/TestOzoneManagerSyncMetrics.java

Purpose: This test verifies that `OzoneManagerSyncMetrics` maintains independent counters for snapshot requests, snapshot failures, delta failures, delta update totals, non-zero delta request counts, average delta updates, and sequence number lag.

Important APIs/types/functions: It uses `OzoneManagerSyncMetrics.create`, `unRegister`, `incrNumSnapshotRequests`, `incrNumSnapshotRequestsFailed`, `incrNumDeltaRequestsFailed`, `incrNumUpdatesInDeltaTotal`, `setSequenceNumberLag`, and the corresponding getters.

Control flow: The test creates a metrics instance, mutates several counters/gauges, asserts exact getter values, and unregisters in a `finally` block to avoid metrics system leakage.

State and persistence behavior: State is in-memory metrics counters and gauges registered with Hadoop metrics. There is no persistence. Cleanup through `unRegister` is important because metrics names are global-ish within the test JVM.

Dependencies and integration points: These metrics are consumed by Recon OM metadata sync monitoring. The test protects the behavior that delta failure increments its own counter and that adding seven updates creates one non-zero delta request with average seven.

Risks: It tests getters directly rather than emitted metrics records. It does not cover zero-update deltas or multiple increments. Metrics registration collisions can occur if `unRegister` is omitted, which the test avoids.

Test signals: Snapshot requests equals one, snapshot failures equals one, delta failures equals one, total delta updates equals seven, non-zero delta requests equals one, average updates per delta request equals `7.0f`, and sequence number lag equals eleven.
