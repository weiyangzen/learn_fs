<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/pom.xml

Purpose: Maven descriptor for `ozone-integration-test-recon`, a jar-packaged module containing Recon integration tests against MiniOzoneCluster, Recon server, SCM/OM APIs, REST endpoints, and admin CLIs.

Important build APIs and dependencies: parent is root `ozone`. Dependencies are almost entirely test scoped and include Jackson, Guava, commons-io, JAX-RS, Hadoop common/HDFS client, Apache HTTP client/core, HDDS client/common/config/container/interface/server/SCM/test utilities, Ozone admin/client/common/integration-test test-jar/interface-storage/manager test-jar/mini-cluster/recon/reconcodegen, Ratis common/server test-jar, and slf4j-api.

Control flow and integration: SpotBugs points at the empty local exclude filter. Compiler disables annotation processing. Maven dependency plugin ignores selected Mockito declarations inherited or used elsewhere.

State and persistence: no runtime state; defines test classpath. Tests create MiniOzoneCluster instances, Recon services, Derby Recon DBs, and HTTP/REST clients.

Risks and tests: the module is heavyweight and sensitive to timing because many tests depend on asynchronous Recon/SCM/OM propagation. Broad test-scope dependency set is necessary but can mask unused dependencies. The descriptor itself is covered by Maven build execution rather than unit tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/pom.xml -->
