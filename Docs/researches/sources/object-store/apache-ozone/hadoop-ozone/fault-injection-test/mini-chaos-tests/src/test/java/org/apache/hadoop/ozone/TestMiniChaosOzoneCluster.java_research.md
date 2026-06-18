<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/TestMiniChaosOzoneCluster.java -->
# sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/TestMiniChaosOzoneCluster.java

Final split target: `Docs/researches/sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/TestMiniChaosOzoneCluster.java_research.md`.

## Purpose
Picocli/JUnit harness for running a MiniOzone chaos cluster with configurable node counts, failure timing, bucket layout, replication, and IO load classes. The file has 222 lines and was read in full for this research pass.

## Important APIs, Types, And Functions
Types/classes: `TestMiniChaosOzoneCluster, AllowedBucketLayouts`. Methods and hooks: `init, addFailureClasses, addLoadClasses, setNumDatanodes, setNumManagers, shutdown, startChaosCluster, test`. Test annotations present: `2`.

## Control Flow
Initialization builds the cluster, creates a random volume and bucket settings, constructs load generators, starts scheduled chaos, runs IO for the requested duration, and always shuts down load generators, client, and cluster.

## State And Persistence Behavior
State is mostly test-runtime state: mini-cluster processes, failed-node sets, scheduled futures, executor futures, random key indexes, Ozone buckets/keys/directories, and generated data buffers. Persistence is through Ozone object-store/filesystem writes during the test run.

## Dependencies And Integration Points
imports `java.util.ArrayList`, `java.util.List`, `java.util.concurrent.TimeUnit`, `org.apache.commons.lang3.RandomStringUtils`, `org.apache.hadoop.hdds.cli.GenericCli`, `org.apache.hadoop.hdds.client.DefaultReplicationConfig`, `org.apache.hadoop.hdds.conf.OzoneConfiguration`, `org.apache.hadoop.hdds.utils.IOUtils`.

## Risks And Edge Cases
- Randomized failure and IO ordering can expose flaky timing, quorum, and readiness assumptions.
- Tests are resource-heavy and marked/unhealthy or fault-injection oriented, so CI runtime and host capacity matter.
- Object-store and filesystem APIs must remain behaviorally aligned for mixed operations.

## Test Signals
JUnit signal is explicit: `2` lifecycle/test annotations and assertions in the file exercise the target behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/TestMiniChaosOzoneCluster.java -->
