<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestInputStreamBase.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestInputStreamBase.java

Purpose: This abstract base class provides a shared MiniOzoneCluster and read-stream configuration for chunk, key, and stream-block input tests.

Important APIs/types/functions: Constants define `CHUNK_SIZE`, `FLUSH_SIZE`, `MAX_FLUSH_SIZE`, `BLOCK_SIZE`, and `BYTES_PER_CHECKSUM`. `newCluster` configures bytes per checksum, SCM stale/dead intervals, datanode pipeline limit, RATIS pipeline limit, SCM block size, replication-manager interval, and client block/chunk/flush sizes through `ClientConfigForTesting`. `updateConfig` changes datanode container layout and closes open containers. `setup` and `cleanup` manage cluster lifecycle.

Control flow: Before all tests, `setup` starts a five-datanode cluster and waits for readiness. Subclasses call `getCluster` and `updateConfig` to run layout-specific cases. `closeContainers` scans SCM containers and closes open ones via `TestHelper.waitForContainerClose` so subsequent writes use the new layout. After all tests, the cluster is closed quietly.

State and persistence behavior: Owns the shared cluster and mutates datanode configuration for container layout. It also forces open container closure, which changes SCM/container persistent state to isolate layout tests.

Dependencies and integration points: Supports `TestChunkInputStream`, `TestKeyInputStream`, and `TestStreamBlockInputStream`; integrates with SCM container layout config, replication manager, and client stream sizing.

Risks: Shared cluster lifecycle improves speed but can introduce state coupling between subclass tests. `updateConfig` changes datanode configs at runtime and assumes closing existing containers is sufficient layout isolation.

Test signals: Subclass success implicitly validates this base configuration; failures in cluster setup, container close, or layout switching surface across all read-stream tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestInputStreamBase.java -->
