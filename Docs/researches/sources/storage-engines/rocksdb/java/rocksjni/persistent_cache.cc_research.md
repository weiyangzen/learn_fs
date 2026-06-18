# sources/storage-engines/rocksdb/java/rocksjni/persistent_cache.cc

## Purpose
Implements the native side of `org.rocksdb.PersistentCache`, creating and disposing a C++ `std::shared_ptr<rocksdb::PersistentCache>` for Java callers. The object is used by Java table configuration code to attach a persistent read cache to block-based table options.

## Important APIs, Types, And Functions
`Java_org_rocksdb_PersistentCache_newPersistentCache` receives Java handles for `Env` and `Logger`, a cache directory path, size, and `optimizedForNvm` flag. It calls C++ `NewPersistentCache` and returns a native pointer to a heap-allocated `std::shared_ptr<PersistentCache>`.

`Java_org_rocksdb_PersistentCache_disposeInternalJni` deletes that heap-allocated `std::shared_ptr`, decrementing the C++ shared ownership count. Important dependencies include `rocksdb/persistent_cache.h`, `loggerjnicallback.h`, `portal.h`, `cplusplus_to_java_convert.h`, and the generated JNI header `org_rocksdb_PersistentCache.h`.

## Control Flow
Creation reinterprets `jenv_handle` as `Env*`, copies the Java path to `std::string`, reinterprets `jlogger_handle` as `std::shared_ptr<LoggerJniCallback>*`, allocates a new `std::shared_ptr<PersistentCache>` initialized to `nullptr`, and passes that pointer as the output parameter to `NewPersistentCache`. If path conversion raises a JNI exception it returns `0`. If `NewPersistentCache` returns a non-OK `Status`, it throws a Java `RocksDBException` but still returns the allocated shared-pointer wrapper.

Disposal is a single cast from `jlong` back to `std::shared_ptr<PersistentCache>*` followed by `delete`. The actual cache object remains alive if other C++ options structures copied the shared pointer.

## State And Persistence Behavior
The cache itself is persistent storage under the supplied path and size limit, managed by RocksDB's `PersistentCache` implementation rather than this bridge. This file only manages the Java-visible native handle and shared pointer lifetime. The `optimizedForNvm` boolean is forwarded to cache construction and can change how the underlying cache is tuned for the medium.

The heap-allocated shared-pointer wrapper is the native state owned by Java `PersistentCache`. It can be copied into `BlockBasedTableOptions.persistent_cache` through `table.cc`, allowing options to retain cache ownership independently of the Java wrapper object's native handle.

## Dependencies And Integration Points
The Java constructor in `PersistentCache.java` calls `newPersistentCache`, and `BlockBasedTableConfig.setPersistentCache` later passes the returned handle into table-option construction. `table.cc` dereferences the same handle type and copies the shared pointer into `BlockBasedTableOptions`.

The logger handle is expected to point at a Java-backed `LoggerJniCallback` shared pointer. This lets C++ cache code emit logs through Java logging callbacks. The environment handle determines filesystem behavior for the cache path.

## Risks And Edge Cases
The bridge assumes non-null, valid `Env` and logger handles. A null or already-disposed logger handle would be dereferenced before status handling. Size is cast from signed Java `long` to `uint64_t`; negative values would become very large unless rejected by lower layers.

On `NewPersistentCache` failure, the code throws but returns a non-zero pointer to a shared pointer that may still hold `nullptr`. That matches the common Java pattern only if object construction is aborted and the handle is not used; otherwise callers could retain an invalid native object. The allocation occurs before construction status is known, so exception paths rely on Java wrapper cleanup or process lifetime to avoid leaks. Disposal is not idempotent at the native level; Java must call it once per live handle.

## Test Signals
Coverage is indirect in `BlockBasedTableConfigTest.persistentCache`, which constructs a `PersistentCache`, installs it in `BlockBasedTableConfig`, builds `Options`, and checks the resulting table factory name. Stronger tests would assert creation failure behavior for invalid paths/sizes, logger callback safety, disposal after table options copy the shared pointer, and negative-size handling.
