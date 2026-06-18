<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_options_universal.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/compaction_options_universal.cc

## Purpose
Exposes universal compaction tuning through JNI.

## Important APIs and Types
CompactionOptionsUniversal Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Allocates/deletes `CompactionOptionsUniversal` and maps size ratio, min/max merge width, max size amplification percent, compression size percent, stop style enum, and allow-trivial-move.

## State and Persistence Behavior
State is in-memory options consumed by column-family options; persistence impact is indirect through generated SST layout and compaction scheduling.

## Dependencies and Integration Points
Depends on `CompactionStopStyleJni` conversion. Risks include invalid enum bytes and signed Java values used for unsigned thresholds. Tests should verify Java setters round-trip and a universal-compaction DB opens with the configured options.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_options_universal.cc -->
