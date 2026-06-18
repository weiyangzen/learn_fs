# sources/storage-engines/rocksdb/env/file_system_tracer.cc

## Purpose
Implements the tracing wrappers declared in `file_system_tracer.h`. Each overridden filesystem or file operation delegates to the wrapped implementation, measures elapsed nanoseconds with `StopWatchNano`, creates an `IOTraceRecord`, and writes it through `IOTracer`. The implementation is intentionally transparent: it does not change I/O semantics, only observes status, latency, basename, length, offset, or file size where available.

## Important APIs and Functions
- `FileSystemTracingWrapper::{NewSequentialFile,NewRandomAccessFile,NewWritableFile,ReopenWritableFile,ReuseWritableFile,NewRandomRWFile,NewDirectory,GetChildren,DeleteFile,CreateDir,CreateDirIfMissing,DeleteDir,GetFileSize,Truncate}` trace top-level `FileSystem` operations.
- `FSSequentialFileTracingWrapper::{Read,PositionedRead,InvalidateCache}` traces sequential file data paths and cache invalidation.
- `FSRandomAccessFileTracingWrapper::{Read,MultiRead,Prefetch,InvalidateCache,ReadAsync,ReadAsyncCallback}` traces random reads, batched reads, prefetch, cache invalidation, and async completions.
- `FSWritableFileTracingWrapper::{Append,PositionedAppend,Truncate,Close,GetFileSize,InvalidateCache}` traces write-side operations.
- `FSRandomRWFileTracingWrapper::{Write,Read,Flush,Close,Sync,Fsync}` traces read/write file operations.

## Control Flow
Most methods follow the same sequence: start a timer, call `target()->...`, compute elapsed time, encode fields in `io_op_data`, build an `IOTraceRecord`, call `io_tracer_->WriteIOOp`, then return the original status or result. Data operations set `kIOLen` and/or `kIOOffset`; file-size operations set `kIOFileSize`. `MultiRead` records one trace row per request using each request's individual status. `ReadAsync` allocates callback state, swaps in a wrapper callback, and records the operation only when the underlying async read invokes `ReadAsyncCallback`.

## State and Persistence
The file stores no persistent state. Runtime state consists of wrapper members inherited from the header, per-call timers, and async callback heap state. Trace persistence is delegated to `IOTracer`, so this layer depends on the tracer's lifetime and output policy. Async callback info is deleted after callback execution, and is also deleted if the underlying `ReadAsync` submission immediately fails.

## Dependencies and Integration Points
Depends on `rocksdb/file_system.h`, `rocksdb/system_clock.h`, `rocksdb/trace_record.h`, and `trace_replay/io_tracer.h`. It integrates with RocksDB's filesystem abstraction through wrapper classes and with replay/diagnostics through `IOTraceRecord` and `IOTracer::WriteIOOp`. Debug context is forwarded to both real I/O and trace writing where applicable.

## Risks and Edge Cases
- All implementation methods dereference `io_tracer_` unconditionally; callers must only route through tracing wrappers when a tracer exists and tracing is enabled.
- Several records use requested length (`n`) while others use returned length (`result->size()`), so analysis consumers must understand the per-operation encoding.
- Async tracing lifetime depends on the underlying implementation eventually invoking the callback after accepting the request. If an implementation accepts and later drops a callback, the wrapper leaks callback info and loses a trace event.
- Basename extraction uses `find_last_of("/\\") + 1`; paths without separators produce the full string, which is fine, but trace output intentionally omits directory context.

## Test Signals
No direct tests in this group target `file_system_tracer.cc`. Indirect coverage comes from RocksDB I/O tracing and replay tests elsewhere. Risk-sensitive paths worth testing are async failure cleanup, `MultiRead` per-request status recording, and null/disabled tracer routing through `FileSystemPtr` and file pointer wrappers.
