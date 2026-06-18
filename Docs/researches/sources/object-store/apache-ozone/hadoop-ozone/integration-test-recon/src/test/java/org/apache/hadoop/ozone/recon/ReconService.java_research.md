<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/ReconService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/ReconService.java

Purpose: `MiniOzoneCluster.Service` implementation that embeds a Recon server in integration tests.

Important APIs: constructor allocates free localhost HTTP and datanode addresses and writes Recon address keys. `start(conf)` asserts Recon is not running, resets and sets `ConfigurationProvider`, configures Recon directories and DB URL, creates `ReconServer`, and executes it. `stop()` stops and joins the running server. `toString()` reports live HTTP/HTTPS addresses. `getReconServer()` exposes the server to tests. `configureRecon` sets Recon DB, OM snapshot DB, SCM DB, Derby JDBC URL, safemode wait threshold, and addresses under the cluster metadata directory.

Control flow and integration: MiniOzoneCluster calls `start`/`stop` as an extra service. Tests use `getReconServer` to reach Recon managers, task controllers, HTTP server addresses, and service providers.

State and persistence: stores fixed ports and one mutable `ReconServer`. Persists test Recon data under `<ozone.metadata.dirs>/recon`, including Derby DB and snapshot/SCM DB directories.

Risks and tests: requires `ozone.metadata.dirs` to be set by cluster setup. `start` after `stop` reuses the same address values but reconfigures against the supplied cluster conf, enabling restart tests. Global `ConfigurationProvider` reset can affect other Recon tests in the same JVM. Coverage is indirect through all Recon integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/ReconService.java -->
