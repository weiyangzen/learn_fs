<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/loadgenerators/AgedDirLoadGenerator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/loadgenerators/AgedDirLoadGenerator.java

Final split target: `Docs/researches/sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/loadgenerators/AgedDirLoadGenerator.java_research.md`.

## Purpose
Chaos-test load generator component `AgedDirLoadGenerator` that participates in repeated Ozone bucket/filesystem IO during failure injection. The file has 48 lines and was read in full for this research pass.

## Important APIs, Types, And Functions
Types/classes: `AgedDirLoadGenerator`. Methods and hooks: `AgedDirLoadGenerator, generateLoad, initialize`. Test annotations present: `0`.

## Control Flow
The file runs through test/framework lifecycle methods or direct method calls shown above; assertions and helper calls drive observable behavior.

## State And Persistence Behavior
State is mostly test-runtime state: mini-cluster processes, failed-node sets, scheduled futures, executor futures, random key indexes, Ozone buckets/keys/directories, and generated data buffers. Persistence is through Ozone object-store/filesystem writes during the test run.

## Dependencies And Integration Points
imports `org.apache.commons.lang3.RandomUtils`, `
import org.apache.commons.lang3.RandomUtils`.

## Risks And Edge Cases
- Randomized failure and IO ordering can expose flaky timing, quorum, and readiness assumptions.
- Tests are resource-heavy and marked/unhealthy or fault-injection oriented, so CI runtime and host capacity matter.
- Object-store and filesystem APIs must remain behaviorally aligned for mixed operations.

## Test Signals
Signals come from chaos-test completion, propagated future exceptions, JUnit assertions in `LoadBucket`, mini-cluster readiness waits, and generated test reports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/loadgenerators/AgedDirLoadGenerator.java -->
