<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/failure/Failures.java -->
# sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/failure/Failures.java

Final split target: `Docs/researches/sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/failure/Failures.java_research.md`.

## Purpose
Catalog of chaos failure actions for Ozone managers, SCMs, and datanodes, including restart and start/stop variants with readiness validation. The file has 226 lines and was read in full for this research pass.

## Important APIs, Types, And Functions
Types/classes: `Failures, OzoneFailures, OzoneManagerRestartFailure, OzoneManagerStartStopFailure, ScmFailures, StorageContainerManagerStartStopFailure, StorageContainerManagerRestartFailure, DatanodeFailures, DatanodeRestartFailure, DatanodeStartStopFailure`. Methods and hooks: `getName, getClassList, validateFailure, fail, fail, validateFailure, fail, fail, validateFailure, fail`. Test annotations present: `0`.

## Control Flow
Each nested failure class asks the cluster for eligible nodes, decides restart versus start/stop where relevant, invokes the cluster operation, and relies on superclass validation to wait for readiness.

## State And Persistence Behavior
State is mostly test-runtime state: mini-cluster processes, failed-node sets, scheduled futures, executor futures, random key indexes, Ozone buckets/keys/directories, and generated data buffers. Persistence is through Ozone object-store/filesystem writes during the test run.

## Dependencies And Integration Points
imports `java.util.ArrayList`, `java.util.List`, `java.util.Set`, `org.apache.hadoop.hdds.protocol.DatanodeDetails`, `org.apache.hadoop.hdds.scm.server.StorageContainerManager`, `org.apache.hadoop.ozone.MiniOzoneChaosCluster`, `org.apache.hadoop.ozone.om.OzoneManager`, `org.slf4j.Logger`.

## Risks And Edge Cases
- Randomized failure and IO ordering can expose flaky timing, quorum, and readiness assumptions.
- Tests are resource-heavy and marked/unhealthy or fault-injection oriented, so CI runtime and host capacity matter.
- Object-store and filesystem APIs must remain behaviorally aligned for mixed operations.

## Test Signals
Signals come from chaos-test completion, propagated future exceptions, JUnit assertions in `LoadBucket`, mini-cluster readiness waits, and generated test reports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/failure/Failures.java -->
