<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/clock_cache.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/clock_cache.cc

## Purpose
Creates and disposes Java-owned `std::shared_ptr<rocksdb::Cache>` instances wrapping `NewClockCache`. The sole constructor JNI method is `ClockCache.newClockCache(capacity, shardBits, strictCapacityLimit)`.

## Important APIs and Types
ClockCache Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Control flow is a direct parameter cast to `size_t`, `int`, and `bool`, then allocation of a heap `shared_ptr<Cache>`. Disposal deletes only the wrapper `shared_ptr`, letting shared ownership release the underlying cache when references drain.

## State and Persistence Behavior
No persistence is introduced; state is cache-resident memory and RocksDB cache metadata. Java sees only an opaque handle.

## Dependencies and Integration Points
Integration is with RocksDB's experimental clock cache implementation and Java `Cache` options. Risks include negative Java capacity becoming a huge `size_t`, invalid shard bits, and misuse after disposal. Tests should create with boundary values and verify ColumnFamilyOptions can consume and release the cache.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/clock_cache.cc -->
