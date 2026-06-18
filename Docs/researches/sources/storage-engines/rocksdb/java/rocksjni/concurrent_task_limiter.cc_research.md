<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/concurrent_task_limiter.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/concurrent_task_limiter.cc

## Purpose
Creates and manages `std::shared_ptr<ConcurrentTaskLimiter>` for Java code.

## Important APIs and Types
ConcurrentTaskLimiter Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Constructor converts a Java name to `std::string`, calls `NewConcurrentTaskLimiter`, wraps the shared pointer on heap, and returns it. Accessors expose name, max outstanding task mutation/reset, outstanding task count, and disposal of the wrapper.

## State and Persistence Behavior
Limiter state is shared in memory and can be referenced by RocksDB background work. It does not persist across process restart.

## Dependencies and Integration Points
Depends on `JniUtil` string conversion and RocksDB task limiter API. Risks include null name conversion, negative limits, lifetime while DB options hold shared refs, and concurrency races in user expectations. Tests should validate limit changes under concurrent compaction/flush scheduling.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/concurrent_task_limiter.cc -->
