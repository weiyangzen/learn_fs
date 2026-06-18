# sources/storage-engines/pebble/sstable/valblk/reader.go

## Purpose
Implements lazy fetching of values stored in SSTable value blocks, including access while an SSTable iterator is open and fallback access after iterator closure.

## Important APIs, Types, And Functions
Interfaces `ReaderProvider`, `ExternalBlockReader`, and `IteratorBlockReader` abstract block reads. `blockProviderWhenClosed` bridges closed-iterator lazy fetches. `Reader`, `MakeReader`, `GetInternalValueForPrefixAndValueHandle`, and `Close` implement block value construction. `valueBlockFetcher`, `FetchHandle`, `getValueInternal`, `getBlockHandle`, and `fetcherStats` implement actual fetching and caching.

## Control Flow
When a data block value prefix points to a value block, `Reader` lazily allocates a `valueBlockFetcher`, decodes value length and short attribute, and returns a `LazyValue` carrying the remaining handle. Fetching first reads the value-block index if absent, then reads/caches the referenced value block, slices out the requested value, and updates stats. If the fetcher was closed, it temporarily obtains an external reader through `ReaderProvider` and copies the value into caller-owned storage.

## State And Persistence Behavior
Persistent state is the value-block index and value blocks in the SSTable. Reader state caches the index block and last value block, with buffer handles released on close.

## Dependencies And Integration Points
Integrates with block readers, `base.LazyValue`, iterator stats, block category stats, `valblk.IndexHandle`, and `DecodeRemainingHandle`. Called by the SSTable internal value constructor in `values.go`.

## Risks And Edge Cases
Lazy values may outlive iterators, requiring the closed-reader path. Buffer handle lifetime and release ordering are critical. There is no explicit bounds check before slicing the value from a decoded handle, so corrupted indexes/handles depend on lower-level validation or may panic.

## Test Signals
Covered indirectly through SSTable value-block tests and iterator lazy-value behavior. Stats counters offer runtime signals for separated values and fetched bytes.
