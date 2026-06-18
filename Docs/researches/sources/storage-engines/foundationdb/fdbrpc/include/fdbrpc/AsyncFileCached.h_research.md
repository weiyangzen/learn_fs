# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/AsyncFileCached.h

## Purpose
`AsyncFileCached.h` declares and largely implements an `IAsyncFile` wrapper that adds an in-memory page cache with random or LRU eviction, dirty-page flushing, zero-copy reads, truncate ordering, metrics, and shared open-file tracking.

## Important APIs, Types, and Functions
Core types are `EvictablePage`, `EvictablePageCache`, `AsyncFileCached`, and `AFCPage`. Important APIs include `AsyncFileCached::open`, `read`, `write`, `readZeroCopy`, `releaseZeroCopy`, `truncate`, `changeFileSize`, `sync`, `flush`, `quiesce`, and template `read_write_impl`. `AFCPage` provides `evict`, `orphan`, `write`, `read`, `readZeroCopy`, `releaseZeroCopy`, `readThrough`, `writeThrough`, `flush`, `quiesce`, and `truncate`.

## Control Flow
`open` deduplicates by filename using `openFiles`, opens an uncached/unbuffered underlying file, records size, and returns a cached wrapper. Reads and writes are split into pages by `read_write_impl`; page reads either hit valid cached data or start/merge underlying reads. Writes mark pages dirty, read missing partial pages when needed, and can orphan buffers when zero-copy readers still hold them. `flush` writes dirty pages through, respecting optional rate control. `truncate_impl` serializes truncates and makes writes that extend past the in-flight truncate wait.

## State and Persistence Behavior
Persistent storage remains the wrapped `IAsyncFile`; cache state is in-memory. `AsyncFileCached` tracks file length, previous length, page map, flushable page list, current truncate future/size, rate control, orphaned zero-copy buffers, and many metric handles. `EvictablePageCache` tracks allocated pages globally for a cache instance and evicts randomly or via intrusive LRU.

## Dependencies and Integration Points
It depends on Boost intrusive lists, Flow futures, `IAsyncFile`, knobs, metrics, deterministic random, and network simulation flags. It integrates with the filesystem layer as an `IAsyncFile` implementation and with telemetry through `Int64MetricHandle`.

## Risks and Edge Cases
Correctness depends on careful coordination of `notReading`, `notFlushing`, dirty flags, zero-copy ref counts, and orphaned pages. Eviction may exceed limits if pages are not immediately evictable. `openFiles` is a static weak-future map keyed only by filename and must be erased on open errors. Partial-page writes require valid read-through data, so read failures can poison subsequent waits. LRU intrusive hooks require pages to be removed consistently before destruction.

## Test Signals
Signals include async-file tests elsewhere in the repository, cache metric counters, trace events such as `AFCUnderlyingOpen*`, and the LRU benchmark in this subset for eviction-related support code.
