# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/EventKeeper.java

## Purpose
`EventKeeper` is the instrumentation contract for counting Java binding events such as JNI calls, fetched bytes, range-query fetches, direct-buffer hits/misses, and range-fetch latency.

## Important APIs, Types, And Functions
The interface defines `count`, `increment`, `timeNanos`, `time`, `getCount`, `getTimeNanos`, and `getTime`. Nested `Event` names events and marks time events. `Events` enumerates built-in driver metrics including `JNI_CALL`, `BYTES_FETCHED`, and `RANGE_QUERY_FETCH_TIME_NANOS`.

## Control Flow
Instrumentation-aware classes check for a non-null `EventKeeper`, increment counters before JNI calls, count bytes after marshaling, and record range fetch timing through `timeNanos`.

## State And Persistence Behavior
The interface requires implementations to be thread-safe but stores no state itself. Implementations decide whether metrics remain in memory, are exported, or are aggregated elsewhere.

## Dependencies And Integration Points
It integrates with `FDB.open(..., EventKeeper)`, `FDBDatabase`, `FDBTransaction`, typed future wrappers, range iterators, and `MapEventKeeper`.

## Risks And Edge Cases
Implementations run on application and callback threads, so slow or unsafe implementations can affect query latency. The interface documents time events but does not enforce that only time events are timed.

## Test Signals
Tests should verify expected counters for gets, range fetches, direct-buffer hits/misses, byte accounting, and time conversion through several `TimeUnit`s.
