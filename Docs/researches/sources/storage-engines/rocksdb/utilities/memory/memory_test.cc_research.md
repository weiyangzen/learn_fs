# sources/storage-engines/rocksdb/utilities/memory/memory_test.cc

## Purpose
This test file validates `MemoryUtil::GetApproximateMemoryUsageByType()` across multiple DB instances, column families, memtables, table readers, and caches.

## Important APIs, types, and functions
`MemoryTest` is a test fixture creating per-thread DB paths and holding a deterministic `Random`. `UpdateUsagesHistory()` calls the utility and stores per-usage-type samples. `GetCachePointers()` discovers table cache, row cache, and block caches from each DB, using `DBImpl` test hooks and unwrapping `StackableDB` when needed. `GetApproximateMemoryUsageByType()` combines cache discovery with the utility call.

`SharedBlockCacheTotal` opens ten DBs sharing a block cache, writes/flushed data, reads keys to populate cache/table readers, and verifies table reader usage remains stable when no additional flushes happen.

`MemTableAndTableReadersTotal` opens ten DBs with three CFs each, writes large values to grow memtables, verifies monotonic growth, creates iterators to pin flushed memtables, flushes, verifies unflushed memory decreases while table reader and cache usage grow, then deletes iterators and verifies total memtable usage drops.

## Control flow
Tests perform deterministic writes and flushes, sample usage after operations, and compare consecutive history entries for monotonicity or equality. The second test explicitly creates iterators before flush so immutable memtables remain pinned and still count in total memtable usage.

## State and persistence behavior
Temporary DBs under `test::PerThreadDBPath("memory_test")` are destroyed/recreated per DB id. Usage history is in-memory in the fixture. Column family handles and iterators are manually deleted.

## Dependencies and integration points
The test depends on `DBImpl` internals, `rocksdb/utilities/memory_util.h`, block-based table factory, cache APIs, test harness/utilities, `Random`, and `StackableDB`. It validates integration between public DB properties, internal cache pointers, and the memory utility.

## Risks and edge cases
Assertions depend on approximate memory properties and timing of flush/compaction behavior; options disable auto compactions to reduce nondeterminism. Shared cache accounting relies on de-duplicated cache pointer sets. The test is disabled on release Windows builds through `main()`.

## Test signals
This is the direct regression suite for memory usage aggregation, especially monotonic behavior under writes, flushes, cache fills, and pinned memtables.
