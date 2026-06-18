# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstFileManager.java

## Purpose
`SstFileManager` tracks SST files across one or more RocksDB instances and controls deletion rate and disk-space related write throttling/failures. It is final and documented as thread-safe.

## Important APIs and Types
- Extends `RocksObject`.
- Defaults: delete rate, delete existing trash, max trash/DB ratio, and max delete chunk bytes.
- Constructor chain accepts `Env`, optional `Logger`, deletion rate, max trash ratio, and delete chunk size.
- Space controls: `setMaxAllowedSpaceUsage`, `setCompactionBufferSize`, `isMaxAllowedSpaceReached`, `isMaxAllowedSpaceReachedIncludingCompactions`.
- Tracking: `getTotalSize`, `getTrackedFiles`.
- Deletion throttling: `getDeleteRateBytesPerSecond`, `setDeleteRateBytesPerSecond`, `getMaxTrashDBRatio`, `setMaxTrashDBRatio`.
- Disposal delegates to `disposeInternalJni`.

## Control Flow
Constructors progressively fill defaults and end at a native `newSstFileManager` call using the environment handle, optional logger handle or zero, rate, ratio, and chunk size. Public methods pass the manager native handle to JNI setters/getters. The manager can then be supplied through RocksDB options outside this file to track SST files and enforce limits.

## State and Persistence Behavior
Java state is the native manager pointer. Native state tracks SST file paths/sizes, trash deletion scheduling, deletion rate limiting, max allowed space, and compaction buffer reservation. It influences persistence by delaying or chunking file deletion and by causing writes to fail when tracked SST usage exceeds configured limits.

## Dependencies and Integration Points
It depends on `Env`, `Logger`, `RocksDBException`, `Map`, and native RocksDB SstFileManager. It integrates with DB options that accept an SstFileManager and with filesystem behavior supplied by `Env`.

## Risks
The constant name `MAX_TRASH_DB_RATION_DEFAULT` appears misspelled but is part of the public API. Incorrect `Env` or `Logger` lifetimes can invalidate native construction/use. Space-limit APIs can intentionally make RocksDB writes fail, so operational tests must distinguish expected limit failures from corruption. `getTrackedFiles` returns native-derived paths and sizes whose consistency depends on active DB tracking.

## Test Signals
Tests should cover constructor overload default propagation, invalid native argument handling, total size/tracked file updates after DB writes/compactions, delete-rate setter/getter round trips, max-trash-ratio behavior, max-space-reached behavior including compactions, and thread-safe concurrent getters/setters.
