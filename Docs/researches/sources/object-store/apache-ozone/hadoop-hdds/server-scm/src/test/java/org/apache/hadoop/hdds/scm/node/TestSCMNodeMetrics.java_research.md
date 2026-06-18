# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestSCMNodeMetrics.java

Purpose: verifies metrics exported by `SCMNodeManager` and `SCMNodeMetrics`, including heartbeat counters, node report counters, state gauges, writable-node gauge, and ozone/filesystem capacity gauges.

Important APIs and types: constructs an `SCMNodeManager` directly with `OzoneConfiguration`, `SCMStorageConfig`, `EventQueue`, `NetworkTopologyImpl`, empty `SCMContext`, and mocked `HDDSLayoutVersionManager`. It uses `MetricsAsserts.getMetrics`, `getLongCounter`, and `assertGauge` against `SCMNodeMetrics.SOURCE_NAME`.

Control flow: `@BeforeAll` initializes one registered datanode with a simple node report. Counter tests snapshot a metric, call `processHeartbeat` or `processNodeReport`, and expect the counter to increment. Failure tests send heartbeat or node report for an unregistered random datanode. The gauge test updates storage and filesystem fields, reads metrics, and checks every operational/health-state gauge plus capacity totals.

State and persistence behavior: all state is in-memory for a static node manager. Registration seeds node-state and metric state; report processing mutates per-node storage stats and cluster aggregate metrics. The test closes the manager in `@AfterAll`; no RocksDB persistence is involved.

Dependencies and integration points: depends on Hadoop metrics2, `HddsTestUtils.createStorageReport`, protobuf node reports, SCM layout-version compatibility, and the SCM node manager metrics source registration.

Risks and edge cases: the static node manager means metric state is shared across tests, so tests rely on snapshot-before-action rather than absolute counter values. The gauge test sleeps after a heartbeat, making it sensitive to timing. It intentionally expects `NonWritableNodes` to be 1 because the synthetic datanode lacks metadata-volume space.

Test signals: gives direct signal that successful and failed heartbeat/node-report paths update counters and that the public metrics surface includes all expected node state and capacity gauges.
