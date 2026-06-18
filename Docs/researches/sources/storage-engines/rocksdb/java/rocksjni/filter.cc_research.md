<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/filter.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/filter.cc

## Purpose
Creates and disposes native filter policies, currently Bloom filters.

## Important APIs and Types
Filter policy Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`BloomFilter.createNewBloomFilter(bitsPerKey, useBlockBasedMode)` calls `NewBloomFilterPolicy`, wraps the returned filter policy in `std::shared_ptr<const FilterPolicy>`, and returns a heap pointer to that shared pointer. Generic `Filter.disposeInternalJni` deletes the shared pointer wrapper.

## State and Persistence Behavior
Filter policy state is configuration used by table builders/readers. Persistent impact is indirect: generated SST filter blocks encode the selected policy.

## Dependencies and Integration Points
Depends on RocksDB filter policy API. Risks include invalid bits-per-key, use after disposal while options still refer to the shared policy, and compatibility of persisted SST filter blocks. Tests should open DB with Bloom filter, query misses, and dispose after DB close.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/filter.cc -->
