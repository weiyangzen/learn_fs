<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_filter_factory.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/compaction_filter_factory.cc

## Purpose
Creates and disposes a shared pointer to `CompactionFilterFactoryJniCallback` for Java factories.

## Important APIs and Types
AbstractCompactionFilterFactory bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`createNewCompactionFilterFactory0` allocates a callback with the Java factory object, wraps it in `std::shared_ptr`, then heap-allocates the `shared_ptr` for Java handle storage. Disposal deletes the heap wrapper, reducing shared ownership.

## State and Persistence Behavior
The factory persists as long as RocksDB options keep the shared pointer. It creates per-compaction filter instances through the callback file.

## Dependencies and Integration Points
Integration is with `CompactionFilterFactory` in column-family options. Risks include Java callback exceptions during factory construction and stale Java objects if disposal happens while DB still owns a shared copy. Tests should use Java factories, dispose options/DB in different orders, and verify no callbacks after close.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_filter_factory.cc -->
