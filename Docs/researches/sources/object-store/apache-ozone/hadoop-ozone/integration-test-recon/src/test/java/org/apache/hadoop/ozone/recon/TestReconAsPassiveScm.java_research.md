<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconAsPassiveScm.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconAsPassiveScm.java

Purpose: integration tests for Recon acting as a passive SCM mirror rather than an active SCM command issuer.

Important APIs: `@BeforeEach init` starts a 3-datanode MiniOzoneCluster with Recon and short container/pipeline report intervals. `testDatanodeRegistrationAndReports` waits for Recon pipelines, verifies SCM pipelines exist in Recon, asserts pipeline creation in Recon throws `UnsupportedOperationException`, compares node counts, allocates and writes a container through SCM/datanode pipeline, checks Recon container manager mirrors SCM, and verifies Recon ignores unsupported close-container commands by log capture. `testReconRestart` stops Recon, creates a container and deletes a pipeline in SCM while Recon is down, restarts Recon, verifies nodes are loaded, closed pipeline is absent, and new container appears.

Control flow and integration: exercises Recon's SCM facade, node manager, pipeline manager, container manager, and event queue against a live SCM. Uses `runTestOzoneContainerViaDataNode` to write container data via Xceiver client.

State and persistence: per-test cluster and Recon service. Restart test reuses ReconService addresses and cluster conf; Recon persistent DB path is under cluster metadata.

Risks and tests: waits rely on report intervals and can be timing-sensitive. Log-message assertion couples to exact wording of unsupported command handling. The tests strongly validate passive-mode invariants: no pipeline creation, mirror state, and restart catch-up.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconAsPassiveScm.java -->
