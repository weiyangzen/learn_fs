<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/comparatorjnicallback.h -->
# sources/storage-engines/rocksdb/java/rocksjni/comparatorjnicallback.h

## Purpose
Defines `ReusedSynchronisationType`, `ComparatorJniCallbackOptions`, and the `ComparatorJniCallback` class interface.

## Important APIs and Types
ComparatorJniCallback declarations. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The options record captures direct-buffer use, reuse-buffer use, max reusable size, and synchronization strategy. The class declares RocksDB comparator overrides plus buffer-management helpers and JNI cached fields.

## State and Persistence Behavior
Persistent state is comparator identity/name and Java callback references; reuse buffers are in-memory optimization state. Comparator identity is persisted indirectly in DB metadata through the comparator name.

## Dependencies and Integration Points
This header is the ABI contract for `comparator.cc` and `comparatorjnicallback.cc`. Risks are option default changes, thread-safety policy drift, and mismatched Java bridge signatures. Tests should compile all modes and run DB operations with every reuse/synchronization option.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/comparatorjnicallback.h -->
