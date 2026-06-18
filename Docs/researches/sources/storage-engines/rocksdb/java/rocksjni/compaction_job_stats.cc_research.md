<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_job_stats.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/compaction_job_stats.cc

## Purpose
Provides constructors, mutation helpers, and field accessors for `rocksdb::CompactionJobStats`.

## Important APIs and Types
CompactionJobStats Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`newCompactionJobStats`, `disposeInternalJni`, `reset`, and `add` manage the native struct. Accessors return elapsed time, input/output record and file counts, bytes, deletion/corruption counters, file I/O nanoseconds, output key prefixes, and single-delete diagnostics.

## State and Persistence Behavior
State is a native stats aggregate copied or accumulated in memory. It summarizes compaction work that rewrote persisted SSTs, but does not itself persist anything.

## Dependencies and Integration Points
Depends mainly on `CompactionJobStats` layout and `JniUtil::copyBytes`. Risks are Java/native field drift, unsigned-to-signed narrowing in `jlong`, and null handles. Tests should compare Java values against event-listener stats and verify `reset`/`add` semantics.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_job_stats.cc -->
