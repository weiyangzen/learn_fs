<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestReadRetries.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestReadRetries.java

Purpose: This test validates read retry behavior across a three-node RATIS pipeline and confirms FSO intermediate directory status remains accessible after data-node failures.

Important APIs/types/functions: It configures FSO paths with `configureFSOptimizedPaths`, uses `MiniOzoneCluster`, `OzoneClient`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `TestDataUtil.createKey`, `OzoneClientTestUtils.assertKeyContent`, OM `lookupKey`, SCM `ContainerManager`/`PipelineManager`, and `bucket.getFileStatus`.

Control flow: A 3-datanode cluster is started with one pipeline owner container. The test creates an FSO bucket, writes a nested key under `a/b/c/` with RATIS/THREE, verifies client key details match OM block location, resolves the backing pipeline, and confirms it has three datanodes. It then shuts down datanodes one by one: after the first and second shutdowns, full key content must still read; after the third, reading must throw `IOException`. Finally it verifies the intermediate directory `a/b/c` is returned as a directory with the expected trimmed name.

State and persistence behavior: The test observes OM key block metadata, SCM pipeline membership, datanode process state, and FSO directory metadata.

Dependencies and integration points: Integrates read retry/failover in `KeyInputStream`/client read path, RATIS replicated container reads, SCM metadata lookup, and FSO directory status APIs.

Risks: Sequential datanode shutdown assumes no replacement replicas are created during the short test. Timing changes in replication manager could alter availability expectations.

Test signals: Passing means reads survive loss of up to two replicas in a three-node pipeline and fail only when all replicas are unavailable, while FSO directory metadata remains queryable.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestReadRetries.java -->
