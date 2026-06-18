<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestHybridPipelineOnDatanode.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestHybridPipelineOnDatanode.java

Purpose: This test verifies that RATIS pipelines with different replication factors can coexist on overlapping datanodes and still serve client I/O correctly.

Important APIs/types/functions: It uses `MiniOzoneCluster`, `OzoneClientFactory`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `TestDataUtil.createKey`, `OzoneKeyDetails.getOzoneKeyLocations`, SCM `getContainerInfo`, `PipelineManager.getPipeline`, and standard `bucket.readKey`.

Control flow: A 3-datanode cluster is started with SCM RATIS pipeline limit 5. The test creates a volume/bucket, writes one key with RATIS/ONE and another with RATIS/THREE, resolves each key's container and pipeline ID, and compares pipeline type, node membership, and identity. It asserts the RATIS/ONE pipeline has one node, the RATIS/THREE pipeline is a distinct RATIS pipeline, and the three-node pipeline contains the single-node pipeline's datanode. Finally it reads both keys and compares bytes with the original payload.

State and persistence behavior: Persistent state is limited to key objects, container location metadata, and SCM pipeline records. The test does not mutate local container files; it validates that metadata placement and stored bytes are consistent.

Dependencies and integration points: Integrates client key creation, SCM pipeline allocation for mixed factors, datanode membership accounting, and read path correctness across different replication factors.

Risks: The placement assertion depends on SCM choosing a three-replica pipeline that includes the node selected for the one-replica pipeline. Pipeline policy or limit changes can alter this without breaking client functionality.

Test signals: Passing confirms mixed RATIS factor placement is allowed on the same datanode set and both keys remain readable through the RPC client.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestHybridPipelineOnDatanode.java -->
