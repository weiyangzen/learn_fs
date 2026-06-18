<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/jnicallback.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/jnicallback.cc

## Purpose
Provides shared global-reference and thread-attachment behavior for Java-backed C++ callback classes.

## Important APIs and Types
JniCallback base implementation. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The constructor stores the current `JavaVM` and creates a global ref to the Java callback object. `getJniEnv` and `releaseJniEnv` delegate to `JniUtil` for thread attach/detach tracking. The destructor attaches if needed, deletes the global ref, and releases the environment.

## State and Persistence Behavior
State is a global Java object reference and VM pointer held by native callback objects. This is non-persistent but controls callback object lifetime across RocksDB background threads.

## Dependencies and Integration Points
Used by comparator, logger, event listener, and compaction filter factory callbacks. Risks are destructor execution after JVM teardown, null global refs on OOM, and mismatched attach/detach flags. Tests should create callbacks invoked from background threads and dispose them without leaks.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/jnicallback.cc -->
