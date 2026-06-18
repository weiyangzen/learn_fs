# sources/storage-engines/rocksdb/include/rocksdb/utilities/memory_util.h

## Purpose
Declares approximate memory usage aggregation across DB instances and explicit cache sets.

## Important APIs, Types, And Functions
`MemoryUtil::UsageType` categorizes memtable total, unflushed memtables, table readers, and cache usage. `GetApproximateMemoryUsageByType` is templated over DB pointer container element type and returns a usage map.

## Control Flow, State, And Persistence
The implementation queries input DBs for memtable/table-reader usage and separately sums caches provided in `cache_set`. It is read-only and returns a point-in-time approximation.

## Dependencies And Integration Points
Depends on `Cache`, `DB`, `Status`, and STL containers. Integrates with monitoring and memory tuning tools.

## Risks And Edge Cases
DB-internal cache usage is not counted unless the cache is explicitly in `cache_set`. Concurrent DB activity can change values while measuring. Copying the cache set has minor overhead, and callers can double count shared caches if they build the set incorrectly.

## Test Signals
Cover empty inputs, raw and smart DB pointers, cache-only measurements, shared cache deduplication, writes/flushes/table readers, and all usage categories.
