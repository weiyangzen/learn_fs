# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/AsyncUtil.java

## Purpose
`AsyncUtil` provides utility functions for composing `CompletableFuture`s and consuming/mapping `AsyncIterable`/`AsyncIterator` streams without blocking.

## Important APIs, Types, And Functions
Constants `DONE`, `READY_TRUE`, and `READY_FALSE` avoid repeated completed-future allocation. Utilities include `applySafely`, `forEach`, `forEachRemaining`, `collect`, `collectRemaining`, `mapIterable`, two `mapIterator` overloads, `whileTrue`, `success`, `whenReady`, `composeExceptionally`, `composeHandle`, `composeHandleAsync`, `getAll`, `tag`, `whenAny`, and `whenAll`. `LoopPartial` implements stack-safe asynchronous looping.

## Control Flow
Iteration helpers call `onHasNext`, process an item, and loop via `whileTrue`. Mapping wrappers delegate iterator state to underlying iterators while applying a synchronous function in `next`. Composition helpers adapt Java `CompletableFuture.handle` forms that return nested futures. `whileTrue` runs synchronously through already-completed futures and schedules continuations only when needed.

## State And Persistence Behavior
The class is stateless aside from static completed futures. Per-call accumulator lists and loop objects are local.

## Dependencies And Integration Points
It depends on `FDB.DEFAULT_EXECUTOR`, Java futures, executors, and functional interfaces. `FDBDatabase` retry loops, `RangeQuery`, `MappedRangeQuery`, and `LocalityUtil` rely on it.

## Risks And Edge Cases
`applySafely` catches only `RuntimeException`, not `Error` or checked exceptions thrown through sneaky mechanisms. `getAll` uses `getNow(null)` after `whenAll`, so exceptional inputs propagate through `whenAll`. Empty `whenAny` behavior follows `CompletableFuture.anyOf` with an empty array and may never complete.

## Test Signals
Tests should cover sync and async loop bodies, exceptional futures, iterator collection/mapping, closeable iterator mapping preserving close, compose-handle flattening, empty and failing task collections, and default/custom executor scheduling.
