<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_options.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/compaction_options.cc

## Purpose
Exposes native `rocksdb::CompactionOptions` for manual compaction calls.

## Important APIs and Types
CompactionOptions Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The file allocates/deletes the options struct and maps compression type, output file size limit, and max subcompactions through simple getters/setters. Compression uses `CompressionTypeJni` enum conversion.

## State and Persistence Behavior
Options state is in-memory and affects future compaction output layout/compression. It has no standalone persistence.

## Dependencies and Integration Points
Integration is with Java manual compaction APIs. Risks include enum drift, negative size/subcompaction values cast to unsigned or wider native types, and options used after disposal. Tests should validate manual compaction observes compression and file-size choices.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_options.cc -->
