<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_options_fifo.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/compaction_options_fifo.cc

## Purpose
Wraps `rocksdb::CompactionOptionsFIFO` for FIFO compaction style configuration.

## Important APIs and Types
CompactionOptionsFIFO Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
JNI methods allocate the struct, expose `max_table_files_size`, `allow_compaction`, `max_table_files_size`/`max_data_files_size`, `ttl`, and `age_for_warm`, plus `use_kv_ratio_compaction`, then delete the struct on dispose.

## State and Persistence Behavior
The struct is transient configuration that influences future FIFO compaction and file deletion. Persistent effects are indirect through RocksDB deciding which SSTs to keep or compact.

## Dependencies and Integration Points
Depends on RocksDB options layout. Risks include Java values outside native ranges and field-name/API drift. Tests should run FIFO-style DBs with configured limits and verify compaction/deletion behavior.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_options_fifo.cc -->
