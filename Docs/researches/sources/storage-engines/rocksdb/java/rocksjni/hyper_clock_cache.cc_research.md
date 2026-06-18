<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/hyper_clock_cache.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/hyper_clock_cache.cc

## Purpose
Creates and disposes `std::shared_ptr<Cache>` wrapping `HyperClockCacheOptions::MakeSharedCache`.

## Important APIs and Types
HyperClockCache Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Constructor fills options from capacity, estimated entry charge, shard bits, memory allocator handle, and strict capacity limit; then returns a heap shared pointer. Disposal deletes the shared pointer wrapper.

## State and Persistence Behavior
State is in-memory cache state. The optional memory allocator may be shared external state and must outlive cache creation/use.

## Dependencies and Integration Points
Depends on hyper clock cache API and memory allocator handle convention. Risks include null or stale allocator handles, negative capacity/charge casts, and option compatibility across RocksDB versions. Tests should construct with and without allocator and run block-cache reads.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/hyper_clock_cache.cc -->
