# sources/storage-engines/rocksdb/utilities/memory/memory_util.cc

## Purpose
This file implements `MemoryUtil::GetApproximateMemoryUsageByType()`, aggregating approximate RocksDB memory consumption by category across a vector of DB handles and an explicit set of cache pointers.

## Important APIs, types, and functions
The templated `GetApproximateMemoryUsageByType()` accepts `std::vector<DBPtr>`, an `unordered_set<const Cache*>`, and an output map keyed by `MemoryUtil::UsageType`. It explicitly instantiates for `DB*` and `std::unique_ptr<DB>`.

It reads `DB::Properties::kSizeAllMemTables` into `kMemTableTotal`, `DB::Properties::kCurSizeAllMemTables` into `kMemTableUnFlushed`, and `DB::Properties::kEstimateTableReadersMem` into `kTableReadersTotal`. It sums `Cache::GetUsage()` for non-null cache pointers into `kCacheTotal`.

## Control flow
The function clears the output map, loops through DBs for each property category, conditionally adds values only when `GetAggregatedIntProperty()` succeeds, then loops through caches and adds their current usage.

## State and persistence behavior
No state is persisted or cached. The returned map is a snapshot of approximate property values and cache usage at call time.

## Dependencies and integration points
It depends on `rocksdb/utilities/memory_util.h`, `db/db_impl/db_impl.h`, `DB` property names, and the `Cache` interface. Callers must provide a de-duplicated cache set to avoid double-counting shared caches.

## Risks and edge cases
The cache set is passed by value, which copies the set. Missing or unsupported DB properties silently contribute zero. Approximate values can change concurrently with DB activity. The utility does not discover caches itself, so caller omissions or duplicate pointers determine accuracy.

## Test signals
`memory_test.cc` validates monotonic and stable behavior across memtables, table readers, and shared caches.
