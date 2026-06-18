<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/env_options.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/env_options.cc

## Purpose
Wraps `rocksdb::EnvOptions`, including construction from defaults or `DBOptions`, file I/O flags, sync/readahead sizes, buffer sizes, and rate limiter pointer.

## Important APIs and Types
EnvOptions Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
JNI methods allocate from default constructor or `DBOptions`, delete the struct, and expose mmap/direct read/write booleans, fallocate, close-on-exec, bytes-per-sync, keep-size fallocate, compaction readahead, writable-file buffer size, and rate limiter assignment.

## State and Persistence Behavior
State is transient file I/O configuration passed into RocksDB file operations. It affects how persisted SST/WAL files are opened and written but does not persist itself.

## Dependencies and Integration Points
Depends on `EnvOptions`, `DBOptions`, and rate-limiter handle conventions. Risks include dangling `RateLimiter*`, platform-specific unsupported flags, and negative Java sizes cast to `size_t`/`uint64_t`. Tests should round-trip fields and exercise direct/mmap options where supported.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/env_options.cc -->
