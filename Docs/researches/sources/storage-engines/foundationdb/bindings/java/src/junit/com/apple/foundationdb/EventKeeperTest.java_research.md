# sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/EventKeeperTest.java

## Purpose
`EventKeeperTest` verifies Java-side event/instrumentation accounting for range queries and contains disabled checks for JNI call counting around native transaction operations.

## Important APIs, Types, and Functions
It uses `EventKeeper`, `MapEventKeeper`, `Events`, `RangeQuery`, `FakeFDBTransaction`, `AsyncIterator`, `KeyValue`, and `ByteArrayUtil`. Disabled tests instantiate `FDBTransaction` directly and expect `UnsatisfiedLinkError`.

## Control Flow
The active test creates a `MapEventKeeper`, a fake transaction backed by one key-value pair, constructs a `RangeQuery`, iterates all results, validates returned key/value content, computes expected byte accounting, and asserts range fetch, record count, and byte count events. Disabled tests would call native methods without a loaded library to count JNI calls.

## State and Persistence Behavior
All state is in-memory. The fake transaction avoids native resources, and the event keeper accumulates counters for the test.

## Dependencies and Integration Points
It integrates with Java range query iteration and event instrumentation. It depends on `FakeFDBTransaction` modeling range results enough for `RangeQuery`.

## Risks and Edge Cases
The disabled tests mention that ctest library loading can make them segfault, so native instrumentation coverage is intentionally absent in normal runs. Active coverage uses only a single key-value row and one range fetch.

## Test Signals
Passing shows that Java range iteration records fetch count, fetched record count, and byte accounting as expected on the fake transaction path.
