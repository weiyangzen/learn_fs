<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compact_range_options.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/compact_range_options.cc

## Purpose
Wraps `rocksdb::CompactRangeOptions` with extra native storage for pointer fields Java cannot safely own directly: `full_history_ts_low` and `canceled`.

## Important APIs and Types
CompactRangeOptions Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The custom `Java_org_rocksdb_CompactRangeOptions` object contains the real options plus a `std::string` timestamp buffer and `std::atomic<bool>`. JNI getters/setters map booleans, integer levels, path ids, subcompactions, `BottommostLevelCompaction`, timestamp start/range encoded with fixed64, and cancellation state. The constructor returns the address of the embedded `compactRangeOptions`; disposal reconstructs the wrapper pointer and deletes it.

## State and Persistence Behavior
State is purely in-memory options consumed later by manual compaction calls. `canceled` can be observed by RocksDB while compaction runs, so atomic storage and lifetime are important.

## Dependencies and Integration Points
Depends on `rocksdb/options.h`, `portal.h` enum helpers, and `util/coding.h`. Major risk: `set_full_history_ts_low` allocates a new `Slice` each call without freeing the previous one, and returning the embedded field pointer relies on it being the first member. Tests should cover timestamp round trip, cancellation during compaction, and leak checks for repeated setters.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compact_range_options.cc -->
