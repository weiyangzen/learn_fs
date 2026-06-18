# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/ProtocolMessageMetrics.java

## Purpose
`ProtocolMessageMetrics<KEY>` collects per-message-type count and total duration metrics for enum-keyed protocol operations. It also tracks current concurrency using an auto-closeable measurement scope.

## Important APIs and Types
`create` and the constructor initialize a `Stats` entry for every enum constant. `increment(KEY, duration)` adds an observed duration. `measure(KEY)` increments concurrency, captures monotonic start time, and returns an `UncheckedAutoCloseable` that decrements concurrency and records elapsed time on close. `register`, `unregister`, and `getMetrics` integrate with Metrics2.

## Control Flow and State
The state is an immutable enum-to-`Stats` map and atomic counters. `getMetrics` emits a record for each key tagged with `type`, plus a separate record for concurrency. `Stats` uses `AtomicLong` counters for call count and cumulative time.

## Persistence, Dependencies, and Integration
No persistent state exists. Dependencies include Hadoop Metrics2, `DefaultMetricsSystem`, `Interns`, `Time.monotonicNow`, and Ratis `UncheckedAutoCloseable`. Callers typically wrap protocol handler bodies in try-with-resources using `measure`.

## Risks and Test Signals
If callers do not close the returned scope, concurrency remains inflated and duration is lost. Passing a null or foreign enum key will fail through the map lookup. Tests should cover all enum constants exported, duration accumulation, concurrent measurements, unregister behavior, and try-with-resources correctness on exceptions.
