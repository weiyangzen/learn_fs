<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/loggerjnicallback.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/loggerjnicallback.cc

## Purpose
Implements RocksDB `Logger` by forwarding log records to a Java `Logger` callback.

## Important APIs and Types
LoggerJniCallback implementation. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The constructor caches the Java `log` method and global refs for all `InfoLogLevel` enum constants. `Logv(level, format, ap)` filters by current log level, formats the varargs message with `vsnprintf`, attaches the thread, creates a Java string, calls Java, describes exceptions, and deletes locals. JNI methods create a shared pointer wrapper, set/get log level, and dispose it. Destructor deletes enum global refs.

## State and Persistence Behavior
Logger state is in-memory level plus Java callback/global enum refs. It observes RocksDB operations but does not persist logs itself unless Java does.

## Dependencies and Integration Points
Depends on `JniCallback`, `LoggerJni`, and `InfoLogLevelJni`. Risks are formatting failures/OOM, Java exceptions being printed not propagated, callback during DB background threads, and global ref cleanup after JVM teardown. Tests should log at every level, change thresholds, and force Java callback exceptions.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/loggerjnicallback.cc -->
