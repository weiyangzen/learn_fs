<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestNSSummaryAdmin.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestNSSummaryAdmin.java

Purpose: integration test for Ozone admin namespace summary/du/quota/dist CLIs against a Recon-enabled MiniOzoneCluster.

Important APIs: `@BeforeAll init` creates `OzoneAdmin`, enables FSO paths, sets Recon address, starts a cluster without datanodes plus `ReconService`, creates one random volume with OBS and FSO buckets. Tests execute namespace CLI commands on root, volume, FSO bucket, and OBS bucket paths. `executeAdminCommands` runs `namespace summary`, `namespace du`, recursive/file-name/length `du`, `namespace quota`, and `namespace dist`.

Control flow and integration: extends `StandardOutputTestBase` to capture CLI output. Assertions check absence of invalid volume/bucket errors and presence of empty-data guidance text. OBS test currently checks general output but does not assert the warning mentioned in its comment.

State and persistence: static cluster/client/store/admin and random names across test methods. Captured output is per method through base class. Cluster metadata is test-local.

Risks and tests: no datanodes means commands test namespace metadata paths, not storage data. Output assertions are broad and may miss formatting regressions. The OBS warning comment and assertion are inconsistent. Static cluster shared across tests can retain output-independent namespace state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestNSSummaryAdmin.java -->
