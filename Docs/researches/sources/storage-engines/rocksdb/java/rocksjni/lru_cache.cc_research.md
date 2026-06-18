<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/lru_cache.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/lru_cache.cc

## Purpose
Creates and disposes Java-owned shared pointers to RocksDB LRU cache instances.

## Important APIs and Types
LRUCache Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`newLRUCache` calls `NewLRUCache` with capacity, shard bits, strict capacity, high-priority pool ratio, default allocator/adaptive mutex/metadata charge policy, and low-priority pool ratio. It returns a heap `std::shared_ptr<Cache>*`; disposal deletes the wrapper.

## State and Persistence Behavior
State is in-memory cache contents and metadata. It is shared through options but not persisted.

## Dependencies and Integration Points
Depends on `cache/lru_cache.h`. Risks include negative capacity/shard bits, ratio validation left to RocksDB, and lifetime while DB options/DB hold shared references. Tests should use high/low-priority pools and verify no leak/double delete on option disposal.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/lru_cache.cc -->
