<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/comparatorjnicallback.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/comparatorjnicallback.cc

## Purpose
Implements RocksDB `Comparator` by calling Java comparator methods, including optimized direct-buffer reuse paths.

## Important APIs and Types
ComparatorJniCallback implementation. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The constructor caches class refs, method IDs, Java name, and optional reusable buffers. `Compare` prepares buffers, optionally locks based on reuse synchronization mode, calls Java `compareInternal`, checks exceptions, and returns the result. `FindShortestSeparator` and `FindShortSuccessor` call Java bridge methods and copy changed bytes back into C++ strings. Helper methods allocate/reuse/delete direct byte buffers.

## State and Persistence Behavior
State includes global refs, method IDs, cached name, callback object, optional buffers, thread-local buffer holders, and mutex/unsafe reuse policy. Comparator decisions shape all persisted key ordering in SSTs and memtables.

## Dependencies and Integration Points
Dependencies include `JniCallback`, `portal.h`, `ByteBufferJni`, and `port::Mutex`. Risks are Java exception handling inside `noexcept` comparator paths, local/global ref leaks, invalid direct buffer lifetimes, comparator inconsistency, and synchronization mode misuse. Tests should stress concurrent comparison, separator/successor mutation, exception callbacks, and direct vs byte-array modes.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/comparatorjnicallback.cc -->
