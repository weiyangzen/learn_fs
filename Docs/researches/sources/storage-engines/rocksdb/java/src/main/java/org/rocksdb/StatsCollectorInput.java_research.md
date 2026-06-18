# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StatsCollectorInput.java

## Purpose
`StatsCollectorInput` is a small holder pairing one `Statistics` object with the callback that should receive samples from it.

## Important APIs and Types
The constructor stores `Statistics` and `StatisticsCollectorCallback`; getters are `getStatistics()` and `getCallback()`.

## Control Flow
There is no branching or native logic. `StatisticsCollector` reads each input in its polling loop.

## State and Persistence Behavior
It is immutable after construction but stores references directly. It performs no lifecycle management; callers must keep the statistics and callback valid.

## Dependencies and Integration Points
It integrates only with `StatisticsCollector` and the callback interface.

## Risks and Test Signals
Tests should cover null handling expectations and lifecycle hazards, especially disposing a `Statistics` instance before collector shutdown. If nulls are passed, failures occur later in the collector loop rather than at construction.
