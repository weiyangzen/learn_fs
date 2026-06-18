<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/comparator.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/comparator.cc

## Purpose
Creates a native `ComparatorJniCallback` for Java comparators and exposes whether the callback uses direct buffers.

## Important APIs and Types
AbstractComparator Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`createNewComparator` builds `ComparatorJniCallbackOptions` from Java booleans/enum values, allocates the callback, wraps it in `std::shared_ptr<Comparator>`, and returns the wrapper pointer. `usingDirectBuffers` reads callback options from an existing handle. Native comparator disposal deletes the shared pointer wrapper.

## State and Persistence Behavior
Comparator state is long-lived in DB/column-family options and affects key ordering, SST layout, and read correctness. It must outlive every DB component that uses it.

## Dependencies and Integration Points
Depends on `comparatorjnicallback.*` and Java bridge method IDs. Risks are catastrophic if Java comparison is inconsistent, if disposal outpaces DB use, or if direct-buffer reuse is unsafely synchronized. Tests need comparator ordering, DB reopen with comparator name, and concurrent read/write paths.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/comparator.cc -->
