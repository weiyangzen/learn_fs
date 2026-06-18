<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_filter_factory_jnicallback.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/compaction_filter_factory_jnicallback.cc

## Purpose
Implements the C++ `CompactionFilterFactory` subclass that calls Java for `name()` and `createCompactionFilter()`.

## Important APIs and Types
CompactionFilterFactory JNI callback implementation. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The constructor caches Java method IDs and copies the factory name. `Name()` returns the cached C string. `CreateCompactionFilter` attaches the current thread as needed, calls the Java factory with context arguments, reads the returned Java filter's native handle, wraps it as `std::unique_ptr<CompactionFilter>`, and releases the JNI environment.

## State and Persistence Behavior
Persistent state is the global Java factory reference inherited from `JniCallback`, cached method ids, and cached name. Each created filter becomes native-owned by RocksDB compaction for that compaction run.

## Dependencies and Integration Points
Depends on `portal.h` factory/filter helpers and `JniCallback`. Risks are exception handling from Java callbacks, returned null filters, ownership transfer of a Java-created native handle, and thread attach/detach correctness. Tests should force Java factory exceptions and verify compaction handles null or thrown callbacks predictably.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_filter_factory_jnicallback.cc -->
