<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/failure/FailureManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/failure/FailureManager.java

Final split target: `Docs/researches/sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/failure/FailureManager.java_research.md`.

## Purpose
Scheduled failure coordinator that periodically chooses one configured `Failures` implementation, applies it to the chaos cluster, and validates cluster readiness afterward. The file has 99 lines and was read in full for this research pass.

## Important APIs, Types, And Functions
Types/classes: `FailureManager`. Methods and hooks: `FailureManager, fail, start, stop, isFastRestart, getBoundedRandomIndex`. Test annotations present: `0`.

## Control Flow
A single-thread scheduled executor runs `fail()` at fixed delay, picks a random configured failure class, applies it, waits for/validates cluster readiness, and cancels plus shuts down during stop.

## State And Persistence Behavior
State is mostly test-runtime state: mini-cluster processes, failed-node sets, scheduled futures, executor futures, random key indexes, Ozone buckets/keys/directories, and generated data buffers. Persistence is through Ozone object-store/filesystem writes during the test run.

## Dependencies And Integration Points
imports `java.util.ArrayList`, `java.util.List`, `java.util.Set`, `java.util.concurrent.Executors`, `java.util.concurrent.ScheduledExecutorService`, `java.util.concurrent.ScheduledFuture`, `java.util.concurrent.TimeUnit`, `org.apache.commons.lang3.RandomUtils`.

## Risks And Edge Cases
- Randomized failure and IO ordering can expose flaky timing, quorum, and readiness assumptions.
- Tests are resource-heavy and marked/unhealthy or fault-injection oriented, so CI runtime and host capacity matter.
- Object-store and filesystem APIs must remain behaviorally aligned for mixed operations.

## Test Signals
Signals come from chaos-test completion, propagated future exceptions, JUnit assertions in `LoadBucket`, mini-cluster readiness waits, and generated test reports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/java/org/apache/hadoop/ozone/failure/FailureManager.java -->
