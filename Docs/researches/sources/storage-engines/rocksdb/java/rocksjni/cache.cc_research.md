<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/cache.cc -->
# Research: sources/storage-engines/rocksdb/java/rocksjni/cache.cc

Purpose: Implements JNI accessors for Java `Cache` usage metrics backed by C++ `std::shared_ptr<rocksdb::Cache>`.

Important APIs/types/functions: `Java_org_rocksdb_Cache_getUsage` and `Java_org_rocksdb_Cache_getPinnedUsage` reinterpret the handle as `std::shared_ptr<Cache>*` and call `GetUsage` or `GetPinnedUsage`.

Control flow: Each function performs a pointer cast, dereferences the shared pointer, calls the native cache metric, and returns the value as `jlong`.

State and persistence behavior: The functions only read in-memory cache accounting. They do not mutate cache contents or persistent DB state.

Dependencies and integration points: Depends on generated `org_rocksdb_Cache.h`, `rocksdb/advanced_cache.h`, and Java cache wrapper objects such as LRU/clock cache classes that own shared pointers.

Risks and edge cases: Invalid or disposed handles cause undefined behavior. Metric values are cast to signed Java long; extremely large usage values would need to fit in `jlong`.

Test signals: Cache-related Java tests should allocate cache-backed options, perform reads/writes, compare usage/pinned usage trends, and run under JNI checking to catch disposed-handle calls.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/cache.cc -->
