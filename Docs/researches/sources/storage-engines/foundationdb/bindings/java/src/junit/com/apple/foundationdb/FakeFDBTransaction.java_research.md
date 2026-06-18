# sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/FakeFDBTransaction.java

## Purpose
`FakeFDBTransaction` is an in-memory subclass of `FDBTransaction` used by unit tests to exercise Java transaction/range-query logic without a running FoundationDB server or native calls.

## Important APIs, Types, and Functions
It stores a `NavigableMap<byte[], byte[]>`, constructors for map/collection/list backing data, overrides `get`, `getRange_internal`, `closeInternal`, `close`, and `finalize`, and exposes `getNumRangeCalls`.

## Control Flow
Constructors copy supplied key-values into a `TreeMap` using `ByteArrayUtil.comparator`. `get` returns a completed future from the backing map. `getRange_internal` increments a call counter, derives a submap from begin/end `KeySelector`s, optionally reverses it, returns a custom `FutureResults` whose `getResults` materializes `KeyValue` objects until row or target-byte limits are reached, then completes the future immediately.

## State and Persistence Behavior
State is in-memory only: backing data and range-call count. Native pointer values are dummy constructor inputs, and close/finalize are no-ops to avoid native destruction.

## Dependencies and Integration Points
It integrates with `RangeQuery`, `FutureResults`, `RangeResult`, and unit tests such as `RangeQueryTest` and `EventKeeperTest`.

## Risks and Edge Cases
The TODO notes that key-selector semantics are incomplete; the implementation uses only key bytes and `orEqual`, ignoring selector offsets. Target-byte accounting increments after adding a row, so exact boundary behavior may not match the C API. Because the fake extends a native-backed class, constructor behavior in `FDBTransaction` must remain compatible with dummy pointers.

## Test Signals
Useful signals include range-call count, row-limit behavior, reverse iteration ordering, and Java range iterator behavior independent of the native client.
