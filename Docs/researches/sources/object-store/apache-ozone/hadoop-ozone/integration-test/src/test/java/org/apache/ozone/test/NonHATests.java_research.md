# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/NonHATests.java

Purpose: This abstract harness groups many non-HA integration suites so they run against a single shared `MiniOzoneCluster`. It is the main non-HA aggregation point for filesystem, SCM, pipeline, client RPC, OM, reconfiguration, shell/debug, and replication preference tests.

Important APIs and types: It extends `ClusterForTests<MiniOzoneCluster>` and defines a `TestCase` interface. Nested classes adapt test suites such as `TestOzoneClientMultipartUploadWithFSO`, Ozone FS tests, SCM container/pipeline/MXBean/metrics tests, `TestReplicationConfigPreference`, client RPC tests, CPU metrics, lease recovery, OM list/status/object-store/block-versioning tests, datanode/OM/SCM reconfiguration tests, `TestOzoneDebugShell`, `TestReconfigShell`, and `TestOzoneDebugReplicasVerify`.

Control flow: The harness relies on inherited cluster startup/shutdown. Each nested class extends an existing test class and overrides `cluster()` to return `getCluster()`. There are no test methods directly in this file; JUnit discovers and runs nested suites in the same cluster context.

State and persistence behavior: The shared cluster persists all data created by nested suites during the class lifecycle: keys, buckets, containers, pipelines, multipart uploads, metrics, reconfiguration state, and debug-shell artifacts. State isolation depends on nested tests using unique names and cleanup.

Dependencies and integration points: This file stitches together broad subsystem coverage under one mini cluster. It is a key integration point for tests that implement the local `NonHATests.TestCase` contract, including `TestReconfigShell` and `TestReplicationConfigPreference` in this subset.

Risks: The breadth of nested tests raises cross-test contamination risk. Reconfiguration and debug tests can mutate runtime settings visible to later tests. Failures may be harder to localize because the harness only provides cluster injection and shared lifecycle.

Test signals: The file's signal is successful execution of all nested suites against the shared non-HA cluster, covering FS behavior, SCM/container/pipeline behavior, client RPC behavior, OM metadata behavior, reconfiguration, debug shell, and replication-config precedence.
