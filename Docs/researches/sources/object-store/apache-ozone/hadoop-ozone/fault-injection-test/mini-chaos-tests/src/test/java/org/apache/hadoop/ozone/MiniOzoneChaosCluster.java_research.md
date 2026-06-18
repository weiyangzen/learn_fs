<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/MiniOzoneChaosCluster.java -->
# sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/MiniOzoneChaosCluster.java

Final split target: `Docs/researches/sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/MiniOzoneChaosCluster.java_research.md`.

## Purpose
MiniOzone HA cluster subclass that schedules random OM, SCM, and datanode failures while protecting quorum thresholds and tracking failed components for restart/stop decisions. The file has 401 lines and was read in full for this research pass.

## Important APIs, Types, And Functions
Types/classes: `causes, MiniOzoneChaosCluster, Builder`. Methods and hooks: `MiniOzoneChaosCluster, startChaos, shutdown, waitForClusterToBeReady, Builder, setNumDatanodes, setNumOzoneManagers, setOMServiceID, setSCMServiceID, setNumStorageContainerManagers, addFailures, initializeConfiguration, build, getNumberOfOmToFail, omToFail, shutdownOzoneManager`. Test annotations present: `0`.

## Control Flow
Builder tunes small block/container/heartbeat timings, constructs OM/SCM/datanode services, and returns a cluster; runtime failure selection chooses random eligible nodes while failed sets prevent over-failing quorum-sensitive roles.

## State And Persistence Behavior
State is mostly test-runtime state: mini-cluster processes, failed-node sets, scheduled futures, executor futures, random key indexes, Ozone buckets/keys/directories, and generated data buffers. Persistence is through Ozone object-store/filesystem writes during the test run.

## Dependencies And Integration Points
imports `java.io.IOException`, `java.time.Duration`, `java.util.Collections`, `java.util.HashSet`, `java.util.List`, `java.util.Set`, `java.util.concurrent.TimeUnit`, `java.util.concurrent.TimeoutException`.

## Risks And Edge Cases
- Randomized failure and IO ordering can expose flaky timing, quorum, and readiness assumptions.
- Tests are resource-heavy and marked/unhealthy or fault-injection oriented, so CI runtime and host capacity matter.
- Object-store and filesystem APIs must remain behaviorally aligned for mixed operations.

## Test Signals
Signals come from chaos-test completion, propagated future exceptions, JUnit assertions in `LoadBucket`, mini-cluster readiness waits, and generated test reports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/MiniOzoneChaosCluster.java -->
