# sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/pom.xml

Purpose: Maven descriptor for `ozone-mini-cluster`, the integration-test harness jar for creating in-process Ozone clusters.

Important APIs/types/functions: Configures dependencies needed to instantiate SCM, OM, datanodes, clients, security, Ratis, and test utilities. Skips javadoc. Runs SpotBugs with the module exclude file and disables annotation processing.

Control flow, state, and persistence: Build configuration only, but it assembles runtime dependencies for mini-cluster classes that create temporary metadata, Ratis, DB, HTTP, OM, SCM, and datanode directories during tests.

Dependencies and integration points: Depends on Guava, Commons IO/Lang, Hadoop auth/common, many HDDS modules, Ozone client/common/manager, Ratis common/server API, and SLF4J. The module is used by integration tests and HA mini-cluster variants.

Risks: This module pulls server and test utility dependencies into a test harness; version conflicts can surface as integration-test failures. Since it depends on live OM/SCM/datanode classes, configuration defaults and port allocation are sensitive.

Test signals: Mini-cluster behavior is validated by downstream integration tests that instantiate `MiniOzoneCluster`.
