<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/TestAllMiniChaosOzoneCluster.java -->
# sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/TestAllMiniChaosOzoneCluster.java

Final split target: `Docs/researches/sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/TestAllMiniChaosOzoneCluster.java_research.md`.

## Purpose
JUnit test harness `TestAllMiniChaosOzoneCluster` for the MiniOzone chaos-test suite. The file has 55 lines and was read in full for this research pass.

## Important APIs, Types, And Functions
Types/classes: `TestAllMiniChaosOzoneCluster`. Methods and hooks: `setup, call`. Test annotations present: `2`.

## Control Flow
The file runs through test/framework lifecycle methods or direct method calls shown above; assertions and helper calls drive observable behavior.

## State And Persistence Behavior
State is mostly test-runtime state: mini-cluster processes, failed-node sets, scheduled futures, executor futures, random key indexes, Ozone buckets/keys/directories, and generated data buffers. Persistence is through Ozone object-store/filesystem writes during the test run.

## Dependencies And Integration Points
imports `java.util.concurrent.Callable`, `org.apache.hadoop.hdds.cli.HddsVersionProvider`, `org.apache.hadoop.ozone.failure.Failures`, `org.apache.hadoop.ozone.loadgenerators.LoadGenerator`, `org.junit.jupiter.api.BeforeAll`, `org.junit.jupiter.api.TestInstance`, `picocli.CommandLine`, `
import java.util.concurrent.Callable`.

## Risks And Edge Cases
- Randomized failure and IO ordering can expose flaky timing, quorum, and readiness assumptions.
- Tests are resource-heavy and marked/unhealthy or fault-injection oriented, so CI runtime and host capacity matter.
- Object-store and filesystem APIs must remain behaviorally aligned for mixed operations.

## Test Signals
JUnit signal is explicit: `2` lifecycle/test annotations and assertions in the file exercise the target behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/TestAllMiniChaosOzoneCluster.java -->
