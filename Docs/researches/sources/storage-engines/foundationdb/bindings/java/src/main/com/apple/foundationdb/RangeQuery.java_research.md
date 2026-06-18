# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/RangeQuery.java

## Purpose
`RangeQuery` is the lazy asynchronous iterable for normal range reads, yielding `KeyValue` rows with chunked fetching, prefetch, limits, reverse support, and streaming-mode hints.

## Important APIs, Types, And Functions
It implements `AsyncIterable<KeyValue>`. `asList` optimizes exact mode into one native chunk or collects via iteration. `AsyncRangeIterator` tracks current chunk, next prefetched chunk, outstanding fetch, previous key for remove, row limit, iteration number, begin/end selectors, fetch future, and cancellation. `FetchComplete` processes each native result chunk.

## Control Flow
The iterator starts a first fetch immediately. `onHasNext` observes current chunk state or waits for `nextFuture`. `next` returns buffered rows, starts the next fetch on the first row of a chunk, swaps in prefetched chunks, records metrics, or waits recursively when no row is ready. Fetch completion updates continuation selectors from the last key and closes the `FutureResults`.

## State And Persistence Behavior
Iterator state is synchronized and mutable. Native range futures remain live only until chunk consumption. `remove` clears the last returned key in the underlying transaction; durability depends on later commit.

## Dependencies And Integration Points
It depends on `FDBTransaction.getRange_internal`, `FutureResults`, `RangeResult`, `RangeResultSummary`, `StreamingMode`, `AsyncUtil`, `EventKeeper`, and `KeySelector`.

## Risks And Edge Cases
The query should not span more than a few seconds because it uses the originating transaction. Cancellation assumes active futures exist. Blocking `hasNext` and recursive `next` use `join`, which wraps exceptions. Prefetch state must avoid reentrant fetches.

## Test Signals
Tests should cover exact `asList`, iterator mode, limits, reverse continuation, empty ranges, multi-chunk prefetch, remove, cancellation, fetch failures, and metrics for bytes/fetch counts/timing.
