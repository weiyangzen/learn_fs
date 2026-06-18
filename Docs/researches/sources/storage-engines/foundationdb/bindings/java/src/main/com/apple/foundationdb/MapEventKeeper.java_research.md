# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MapEventKeeper.java

## Purpose
`MapEventKeeper` is a simple thread-safe in-memory `EventKeeper` implementation useful for tests, diagnostics, and lightweight metric collection.

## Important APIs, Types, And Functions
It stores a `ConcurrentMap<Event, Count>`. `count` increments a counter. `timeNanos` increments both count and duration. `getCount` and `getTimeNanos` read current atomic values. `Count` contains two `AtomicLong`s.

## Control Flow
Each recording call uses `computeIfAbsent` to create a counter and then updates atomic fields. Reads return zero for missing events.

## State And Persistence Behavior
All metric state is in memory for the life of the keeper. No reset or export API is provided beyond getters.

## Dependencies And Integration Points
It implements `EventKeeper` and can be passed to `FDB.open` to instrument `FDBDatabase`, transactions, futures, and range iterators.

## Risks And Edge Cases
The map grows for every distinct event key, so custom high-cardinality events can leak memory. Time events are not validated; `timeNanos` works for any event.

## Test Signals
Tests should cover concurrent increments, missing events returning zero, timing count plus duration behavior, and use with built-in range metrics.
