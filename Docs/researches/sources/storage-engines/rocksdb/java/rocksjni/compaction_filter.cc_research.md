<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_filter.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/compaction_filter.cc

## Purpose
Contains the native disposer for Java-backed compaction filters.

## Important APIs and Types
AbstractCompactionFilter disposal bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`AbstractCompactionFilter.disposeInternal` casts the handle to `CompactionFilterJniCallback*` and deletes it. The actual filter logic lives in the callback class elsewhere.

## State and Persistence Behavior
State is callback-owned global Java references and any Java filter object reachable through them. There is no persistence, but compaction may call the filter while files are being rewritten.

## Dependencies and Integration Points
Depends on the callback type and JNI lifecycle discipline. Risk centers on deleting a filter still referenced by an active compaction or shared factory output. Tests should close filters after DB shutdown and exercise filter invocation during compaction.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_filter.cc -->
