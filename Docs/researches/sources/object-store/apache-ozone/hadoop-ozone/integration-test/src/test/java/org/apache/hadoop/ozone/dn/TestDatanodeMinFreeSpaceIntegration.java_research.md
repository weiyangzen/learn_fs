# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/TestDatanodeMinFreeSpaceIntegration.java

Purpose: Integration test verifying datanode storage reports sent to SCM reflect configured soft minimum free-space reservation.

Important APIs, types, and functions: Uses `MiniOzoneCluster`, datanode/SCM storage reports, `OzoneConfiguration`, and SCM/datanode free-space config keys. The main test is `storageReportsAtScmMatchSoftMinFreeSpaceFromConfig`; helper `storageReportsMatchSoftMinFree` compares reported capacity/remaining values with the configured soft min free value.

Control flow: The test builds a mini cluster with datanode minimum free-space configuration, waits for readiness and reports, then polls SCM-visible storage reports until every reported storage location matches the expected capacity accounting. The helper evaluates storage report fields rather than client-visible object behavior.

State and persistence behavior: The cluster creates datanode volume directories and reports their capacity/free-space state through heartbeats. No object data is written; persistence is limited to volume initialization and SCM report state.

Dependencies and integration points: Covers datanode storage report generation, SCM report ingestion, and configuration plumbing for minimum free space. It indirectly validates datanode volume calculations used by placement and allocation decisions.

Risks: Storage capacity and remaining space depend on the host filesystem. Timing depends on report intervals and SCM processing. The test must compare soft-min-adjusted values without assuming exact absolute disk capacity beyond the configured relationship.

Test signals: The primary signal is that SCM storage reports eventually match datanode soft min free-space expectations; failure indicates config not applied, report not propagated, or incorrect accounting.
