# sources/storage-engines/rocksdb/utilities/counted_fs.h

## Purpose
This header declares the counting data structures and `CountedFileSystem` wrapper used to instrument RocksDB filesystem activity.

## Important APIs, Types, and Functions
`OpCounter` stores atomic operation and byte counts and exposes `Reset` and `RecordOp`. `FileOpCounters` stores atomics for opens, closes, deletes, renames, flushes, syncs, dsyncs, fsyncs, directory opens/closes, plus read/write `OpCounter`s. It exposes `Reset`, `PrintCounters`, and `kName`.

`CountedFileSystem` derives from `FileSystemWrapper`, overrides file creation/open methods plus delete/rename, exposes const and mutable `counters()`, `PrintCounters`, `ResetCounters`, and `GetOptionsPtr`.

## Control Flow
The header specifies which filesystem events are counted. Most operation counting is implemented in the `.cc` wrappers; inline `DeleteFile` and `RenameFile` count only successful calls.

## State and Persistence Behavior
Counters are process memory only and atomically updated. The wrapper forwards all real file work to the base filesystem.

## Dependencies and Integration Points
It depends on RocksDB `FileSystem`, `IOStatus`, namespace, and logger declarations. Integration occurs by wrapping an existing filesystem and optionally retrieving counters via the options pointer name.

## Risks and Edge Cases
Counters are approximate instrumentation, not a transaction log. Atomic relaxed ordering is appropriate for counts but means callers should not infer ordering. A caller that bypasses the wrapper or obtains the target filesystem directly will not be counted.

## Test Signals
Tests should verify each exposed counter, reset behavior, string rendering, and options-pointer discovery under single-threaded and simple concurrent workloads.
