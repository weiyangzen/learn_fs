<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_job_info.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/compaction_job_info.cc

## Purpose
Wraps `rocksdb::CompactionJobInfo` for Java event listeners and manual inspection.

## Important APIs and Types
CompactionJobInfo Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Constructs/deletes a native info object and exposes column-family name, status, thread/job ids, input/output levels, input/output file lists, table properties map, compaction reason, compression type, and stats. Maps use `HashMapJni`, Java strings, and `TablePropertiesJni`; stats returns a new copied `CompactionJobStats` handle.

## State and Persistence Behavior
This is an in-memory snapshot of a compaction event. It references file names and table properties describing persisted SST outputs but does not mutate state.

## Dependencies and Integration Points
Depends on status, compression, compaction reason, table properties, and stats converters. Risks include large maps/lists causing OOM, local reference pressure, and stale pointer use after disposal. Tests should validate listener-created info fields for successful and failed compactions.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_job_info.cc -->
