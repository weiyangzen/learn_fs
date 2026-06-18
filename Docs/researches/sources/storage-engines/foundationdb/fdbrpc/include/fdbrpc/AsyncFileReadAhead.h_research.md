# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/AsyncFileReadAhead.h

## Purpose
`AsyncFileReadAhead.h` implements a read-only `IAsyncFile` wrapper that reads larger blocks, prefetches blocks ahead of the requested range, caches block futures, and limits concurrent underlying reads.

## Important APIs, Types, and Functions
The main type is `AsyncFileReadAheadCache` with nested `CacheBlock`. Key methods are static `readBlock`, static `read_impl`, `read`, unsupported `write`/`truncate`, `sync`, `flush`, `size`, unsupported `readZeroCopy`, `releaseZeroCopy`, `debugFD`, and `getFilename`.

## Control Flow
`read_impl` validates the requested range against file size, clips reads at EOF, computes the block range, starts needed block reads plus configured read-ahead blocks, stores futures in `m_blocks`, waits for needed blocks, copies requested byte ranges into the caller buffer, and evicts unpinned cache entries if the cache exceeds the block limit. `readBlock` takes a `FlowLock` permit, reads into a `CacheBlock`, and releases the permit on success or error.

## State and Persistence Behavior
The wrapped file remains the source of persistent data. The wrapper stores block size, read-ahead count, cache limit, concurrency lock, and a map from block number to future `CacheBlock`s. The destructor cancels cached block futures.

## Dependencies and Integration Points
It depends on Flow futures, `IAsyncFile`, and `FlowLock`. It can wrap any read-only async file where sequential or near-sequential reads benefit from prefetch.

## Risks and Edge Cases
The cache is ordered by block number, not LRU, so eviction favors low block numbers when over limit. Future reference counts are used to determine pinned blocks; misuse could retain large blocks longer than expected. `readZeroCopy` is explicitly unsupported. Errors in cached futures cause a block to be restarted on later reads.

## Test Signals
Read-ahead behavior is signaled by correct read results across block boundaries, EOF clipping, concurrent read limiting, and absence of `ReadZeroCopyNotSupported` except when that unsupported API is intentionally called.
