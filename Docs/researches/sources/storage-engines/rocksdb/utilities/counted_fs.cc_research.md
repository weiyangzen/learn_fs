# sources/storage-engines/rocksdb/utilities/counted_fs.cc

## Purpose
This file implements `CountedFileSystem`, a `FileSystemWrapper` that counts file opens, closes, deletes, renames, directory operations, flush/sync/fsync calls, read operations/bytes, and write operations/bytes.

## Important APIs, Types, and Functions
Wrapper classes include `CountedSequentialFile`, `CountedRandomAccessFile`, `CountedWritableFile`, `CountedRandomRWFile`, and `CountedDirectory`. Each wraps the corresponding file object and records counters around reads, writes, close, flush, sync, fsync, range sync, and directory fsync. `FileOpCounters::PrintCounters` renders a human-readable report. `CountedFileSystem` overrides file creation/open methods to wrap successful results.

## Control Flow
Each `New*` method opens the target file through the base filesystem. On success it increments open counters and replaces the result with a counted wrapper. File operation wrappers call through to the target first, then record successful or supported operations. `OpCounter::RecordOp` counts operations unless status is `NotSupported` and counts bytes only when the operation succeeds.

## State and Persistence Behavior
All counters live in atomics inside `FileOpCounters`. The wrapper does not change persisted file contents except by forwarding the caller's operation to the target filesystem. Directory wrappers count close in the destructor if an explicit `Close` was not called.

## Dependencies and Integration Points
It depends on RocksDB FileSystem wrapper classes and exposes counters through `GetOptionsPtr(FileOpCounters::kName())`, allowing other components to retrieve the counter object. It is useful for tests, diagnostics, and performance instrumentation.

## Risks and Edge Cases
Close counting differs by file type: some wrappers count in destructors, some count only explicit successful closes. Sequential and random-access file destructors count closes even without a close status. `RangeSync` increments the generic sync counter, not a separate range-sync counter. `MultiRead` records each request's status and result size, while the aggregate status is otherwise ignored for byte accounting.

## Test Signals
Useful tests open/read/write/delete/rename files through `CountedFileSystem`, check byte counts, verify directory open/close/fsync counts, and confirm counters reset and can be retrieved through `GetOptionsPtr`.
