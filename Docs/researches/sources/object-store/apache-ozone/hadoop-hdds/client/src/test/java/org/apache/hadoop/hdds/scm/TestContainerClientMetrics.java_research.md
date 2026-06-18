## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/TestContainerClientMetrics.java

**Purpose:** Verifies `ContainerClientMetrics` acquisition/release reference counting and write-chunk metric accounting by total, pipeline, and leader datanode.

**Important APIs/types/functions:** `setup()` drains any existing static `referenceCount` before each test. `testRecordChunkMetrics()` calls `ContainerClientMetrics.acquire()`, builds three `Pipeline` instances with distinct `PipelineID` values and two leader `DatanodeID` values, records chunk writes of 10, 20, and 30 bytes, and asserts totals plus per-pipeline/per-leader counters. `testReleaseWithoutUse()` asserts `release()` throws when the reference count is zero. `testAcquireAndRelease()` checks single and double acquire/release transitions. `createPipeline()` constructs an open pipeline using a mocked `ReplicationConfig`.

**Control flow:** The tests exercise both normal reference-count paths and the error branch for releasing without a matching acquire. The metric test drives aggregation by pipeline id and leader id, including two pipelines sharing a leader.

**State and persistence:** Uses and mutates static `ContainerClientMetrics.referenceCount`. Metrics are in-memory counters; no persistence is involved. The `@BeforeEach` reset loop is important because static state can leak across tests.

**Dependencies and integration points:** Depends on HDDS pipeline and datanode ID types, Mockito for `ReplicationConfig`, and JUnit assertions. It integrates with the client write path indirectly by validating the metrics object used by block output streams.

**Risks:** Direct access to package-visible/static `referenceCount` makes the test sensitive to implementation refactors. The cleanup loop assumes repeated `release()` is safe while count is positive. The test does not release the metrics acquired in `testRecordChunkMetrics()`, relying on the next setup to drain.

**Test signals:** Strong signal for counter identity and lifecycle invariants, but limited to write chunk metrics; it does not validate metric registration/unregistration with the Hadoop metrics system.
