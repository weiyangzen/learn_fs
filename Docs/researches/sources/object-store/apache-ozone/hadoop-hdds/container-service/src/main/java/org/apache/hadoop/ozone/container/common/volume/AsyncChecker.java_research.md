<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/AsyncChecker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/AsyncChecker.java

## Purpose

`AsyncChecker` is a generic interface for scheduling asynchronous health checks against `Checkable` targets, used by datanode volume-checking infrastructure. The complete 62-line file was read.

## Important APIs, Types, and Functions

The interface is parameterized as `<K, V>`. `schedule(Checkable<K,V> target, K context)` returns an `Optional<ListenableFuture<V>>` when a check is accepted. `shutdownAndWait(long, TimeUnit)` cancels executing checks and waits for termination.

## Control Flow

Implementations decide whether a target can be scheduled and return an absent optional when not scheduled. Shutdown is expected to first attempt graceful cancellation, then forceful cancellation, waiting after both attempts.

## State and Persistence Behavior

The interface owns no state. Implementations typically own executor services and in-flight check maps. There is no persistence.

## Dependencies and Integration Points

It depends on Guava `ListenableFuture`, HDFS `Checkable`, `ExecutorService` semantics, and datanode volume checker classes.

## Risks and Edge Cases

Callers must handle `Optional.empty()` without assuming a check is in progress. Implementations need careful duplicate scheduling and shutdown semantics to avoid leaking checks or blocking datanode shutdown.

## Test Signals

Implementation tests should cover accepted and rejected schedules, future completion, duplicate target handling, graceful and forceful shutdown, timeout behavior, and interrupt propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/AsyncChecker.java -->
