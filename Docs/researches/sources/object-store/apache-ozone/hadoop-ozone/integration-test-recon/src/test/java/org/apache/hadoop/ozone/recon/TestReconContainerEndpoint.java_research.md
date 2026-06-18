<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconContainerEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconContainerEndpoint.java

Purpose: integration tests for Recon `ContainerEndpoint.getKeysForContainer`, specifically complete key paths for FSO and OBS buckets.

Important APIs: `@BeforeEach init` clears `ContainerKeyMapperHelper` static state, configures default FSO bucket layout and multiple Recon task threads, starts a 3-datanode cluster with Recon, and creates client/store handles. `testContainerEndpointForFSOLayout` creates an FSO bucket, writes a nested key and a bucket-root key, syncs OM to Recon, waits for event buffer and container-key index, asserts bucket layout, queries keys by container id, and validates key name and complete path. `testContainerEndpointForOBSBucket` performs the same for an OBS bucket with a single key. Helpers instantiate `ContainerEndpoint` directly with Recon server managers, wait until required container key counts are indexed, lookup container IDs through OM key location info, and write key data.

Control flow and integration: drives OM/client writes, Recon OM sync, async Recon task processing, container-key mapper state, and endpoint resource logic without issuing HTTP requests. It waits both for event buffer empty and for container-key counts to avoid races where event queue is drained but batch processing has not updated indexes.

State and persistence: per-test cluster/client/store/recon. Static mapper state is explicitly cleared before and after each test.

Risks and tests: endpoint is constructed with null optional dependencies not needed for `getKeysForContainer`; future endpoint changes may require more wiring. Key/container placement assumptions depend on first block location. The test provides good coverage for path reconstruction differences between FSO and OBS layouts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconContainerEndpoint.java -->
