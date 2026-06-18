<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compression_options.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/compression_options.cc

## Purpose
Wraps `rocksdb::CompressionOptions` fields used by Java compression configuration.

## Important APIs and Types
CompressionOptions Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Allocates/deletes the struct and exposes window bits, level, strategy, max dictionary bytes, zstd max train bytes, max dict buffer bytes, zstd dict trainer enablement, and general enabled flag.

## State and Persistence Behavior
All state is in-memory configuration that affects future block compression and dictionary training. Persistent impact is indirect in SST compression format and size.

## Dependencies and Integration Points
Depends on RocksDB compression option fields. Risks are value-range mismatch with specific compression libraries and Java/native field drift. Tests should round-trip setters and create compressed SSTs with zstd dictionary options enabled/disabled.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compression_options.cc -->
