<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/memory_util.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/memory_util.cc

## Purpose
Exposes approximate memory usage by type for sets of DB and cache handles.

## Important APIs and Types
MemoryUtil Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The JNI method converts DB handle arrays via `JniUtil::fromJPointers`, converts cache shared-pointer handles into an unordered set of raw `Cache*`, calls `MemoryUtil::GetApproximateMemoryUsageByType`, constructs a Java `HashMap`, and maps enum keys to boxed bytes and usage values to boxed longs.

## State and Persistence Behavior
State is observational; it reads live DB/cache memory usage and returns a Java map. No persistence.

## Dependencies and Integration Points
Depends on memory util, `HashMapJni`, enum converters, and boxed primitive helpers. Risks include null arrays/handles, caches disposed while queried, non-OK status returning null without Java exception, and local ref cleanup for map entries. Tests should query multiple DBs/caches and validate expected keys are present.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/memory_util.cc -->
