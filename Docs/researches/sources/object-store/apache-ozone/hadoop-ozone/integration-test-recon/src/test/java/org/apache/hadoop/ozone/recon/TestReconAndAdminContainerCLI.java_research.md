<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconAndAdminContainerCLI.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconAndAdminContainerCLI.java

Purpose: integration tests that compare Recon unhealthy-container reporting with SCM replication-manager/admin-container behavior.

Important APIs: static configuration reduces heartbeat/report/dead-node/task intervals and sets Recon/ReplicationManager task intervals. `@BeforeAll init` starts a 5-datanode cluster with Recon, verifies pipelines and nodes are mirrored, creates an FSO bucket, and writes an Ratis THREE key to establish `containerIdR3`. `testMissingContainer` writes an Ratis ONE key, shuts down all datanodes in its pipeline, waits for zero replicas and SCM missing count, compares Recon unhealthy response, then restarts nodes. Parameterized `testNodesInDecommissionOrMaintenance` drives two pipeline nodes through maintenance or decommission states, waits for op-state and replica-count transitions, and repeatedly compares UNDER_REPLICATED and OVER_REPLICATED Recon responses to SCM reports. Helpers fetch `ReplicationManagerReport`, query Recon unhealthy containers, compare counts and sample IDs, create keys, sync Recon DB with OM, wait for container-key mappings, and extract container IDs from OM key locations.

Control flow and integration: this is a full-cluster timing test spanning datanode lifecycle operations, SCM replication manager, Recon passive SCM/container metadata, OM key metadata, and REST endpoint utility calls. `compareRMReportToReconResponse` requires two stable matching polls to avoid transient agreement while systems converge.

State and persistence: static cluster, SCM client, container managers, bucket, and Recon service. Container state changes persist during the class and are repaired where possible by recommission/restart.

Risks and tests: marked flaky for the maintenance/decommission parameterized test. Timing windows are large but still dependent on cluster scheduling. Static shared state means earlier test failures can affect later tests. The tests validate high-value end-to-end behavior and include explicit stabilization logic for HDDS-15223-style drift.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconAndAdminContainerCLI.java -->
