<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_filter_factory_jnicallback.h -->
# sources/storage-engines/rocksdb/java/rocksjni/compaction_filter_factory_jnicallback.h

## Purpose
Declares the bridge class deriving from `JniCallback` and `rocksdb::CompactionFilterFactory`.

## Important APIs and Types
CompactionFilterFactoryJniCallback declaration. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The header exposes a constructor, `Name()`, and `CreateCompactionFilter(const Context&)`, plus private fields for cached `jmethodID`s and factory name.

## State and Persistence Behavior
State consists of JNI global callback ownership inherited from `JniCallback` and cached IDs/name for repeated background compaction calls.

## Dependencies and Integration Points
Integration is consumed by `compaction_filter_factory.cc` and RocksDB option wiring. Risks are ABI/API drift when Java factory methods or RocksDB `Context` change. Header-level tests are compile/link coverage plus Java factory behavior tests.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_filter_factory_jnicallback.h -->
