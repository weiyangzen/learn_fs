# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MappedRangeQuery.java

## Purpose
`MappedRangeQuery` is the lazy asynchronous iterable for mapped range reads, mirroring `RangeQuery` but yielding `MappedKeyValue` rows produced by a server-side mapper.

## Important APIs, Types, And Functions
It implements `AsyncIterable<MappedKeyValue>`. `asList` optimizes exact streaming into one chunk when possible. `iterator()` returns `AsyncRangeIterator`, which tracks current and next chunks, outstanding fetches, row limit, continuation selectors, cancellation, and fetch futures. `FetchComplete` updates chunk state after native completion.

## Control Flow
Construction is passive, but the iterator starts the first fetch. Each chunk request calls `FDBTransaction.getMappedRange_internal`. When a chunk completes, the iterator consumes `MappedRangeResultInfo`, updates remaining row count and begin/end continuation, and prefetches the next chunk on the first `next` call for each current chunk.

## State And Persistence Behavior
Iterator state is mutable and synchronized. Native chunk futures remain open until `FetchComplete` consumes and closes them. `remove` clears the last returned key from the originating transaction.

## Dependencies And Integration Points
It depends on `FDBTransaction`, `KeySelector`, `StreamingMode`, `MappedRangeResult`, `FutureMappedResults`, `AsyncUtil`, and `EventKeeper`.

## Risks And Edge Cases
The TODO notes duplicated logic with `RangeQuery`. Snapshot mapped ranges are blocked by `FDBTransaction.ReadSnapshot`. Cancellation assumes `nextFuture` and `fetchingChunk` are initialized. Byte accounting counts only top-level key/value lengths, not nested range result bytes.

## Test Signals
Tests should cover exact `asList`, iterative chunk prefetch, row limits, reverse iteration, empty results, cancellation, remove semantics, fetch failures, and instrumentation counters.
