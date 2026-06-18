<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/loadgenerators/LoadExecutors.java -->
# sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/loadgenerators/LoadExecutors.java

Final split target: `Docs/researches/sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/loadgenerators/LoadExecutors.java_research.md`.

## Purpose
Thread-pool runner that dispatches random `LoadGenerator` instances for a fixed runtime and propagates failures through failed futures/ExitUtil. The file has 109 lines and was read in full for this research pass.

## Important APIs, Types, And Functions
Types/classes: `provides, LoadExecutors`. Methods and hooks: `LoadExecutors, load, startLoad, waitForCompletion, shutdown`. Test annotations present: `0`.

## Control Flow
Start initializes all generators, submits `numThreads` async loops, each loop randomly chooses a generator until runtime expires, and completion waits on futures while shutdown terminates the executor.

## State And Persistence Behavior
State is mostly test-runtime state: mini-cluster processes, failed-node sets, scheduled futures, executor futures, random key indexes, Ozone buckets/keys/directories, and generated data buffers. Persistence is through Ozone object-store/filesystem writes during the test run.

## Dependencies And Integration Points
imports `java.util.ArrayList`, `java.util.List`, `java.util.concurrent.CompletableFuture`, `java.util.concurrent.ExecutorService`, `java.util.concurrent.Executors`, `java.util.concurrent.TimeUnit`, `org.apache.commons.lang3.RandomUtils`, `org.apache.hadoop.util.ExitUtil`.

## Risks And Edge Cases
- Randomized failure and IO ordering can expose flaky timing, quorum, and readiness assumptions.
- Tests are resource-heavy and marked/unhealthy or fault-injection oriented, so CI runtime and host capacity matter.
- Object-store and filesystem APIs must remain behaviorally aligned for mixed operations.

## Test Signals
Signals come from chaos-test completion, propagated future exceptions, JUnit assertions in `LoadBucket`, mini-cluster readiness waits, and generated test reports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/loadgenerators/LoadExecutors.java -->
