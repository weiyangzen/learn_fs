<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/loadgenerators/LoadGenerator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/loadgenerators/LoadGenerator.java

Final split target: `Docs/researches/sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/loadgenerators/LoadGenerator.java_research.md`.

## Purpose
Base class and registry for chaos-test IO load generators, defining key naming and the `initialize`/`generateLoad` lifecycle. The file has 67 lines and was read in full for this research pass.

## Important APIs, Types, And Functions
Types/classes: `LoadGenerator, NewLoadGen`. Methods and hooks: `getClassList, initialize, toString`. Test annotations present: `0`.

## Control Flow
The file runs through test/framework lifecycle methods or direct method calls shown above; assertions and helper calls drive observable behavior.

## State And Persistence Behavior
State is mostly test-runtime state: mini-cluster processes, failed-node sets, scheduled futures, executor futures, random key indexes, Ozone buckets/keys/directories, and generated data buffers. Persistence is through Ozone object-store/filesystem writes during the test run.

## Dependencies And Integration Points
imports `java.util.ArrayList`, `java.util.List`, `
import java.util.ArrayList`, `import java.util.List`.

## Risks And Edge Cases
- Randomized failure and IO ordering can expose flaky timing, quorum, and readiness assumptions.
- Tests are resource-heavy and marked/unhealthy or fault-injection oriented, so CI runtime and host capacity matter.
- Object-store and filesystem APIs must remain behaviorally aligned for mixed operations.

## Test Signals
Signals come from chaos-test completion, propagated future exceptions, JUnit assertions in `LoadBucket`, mini-cluster readiness waits, and generated test reports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/loadgenerators/LoadGenerator.java -->
