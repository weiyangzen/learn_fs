# sources/storage-engines/rocksdb/env/file_system_tracer.h

## Purpose
Declares RocksDB filesystem/file wrappers that add binary I/O tracing around selected `FileSystem`, `FSSequentialFile`, `FSRandomAccessFile`, `FSWritableFile`, and `FSRandomRWFile` operations. It also declares pointer adapters that choose the tracing wrapper only when `IOTracer::is_tracing_enabled()` is true, avoiding wrapper overhead in the disabled case.

## Important APIs and Types
- `FileSystemTracingWrapper : FileSystemWrapper` wraps a full `FileSystem` and overrides selected creation, directory, deletion, size, and truncate calls.
- `FileSystemPtr` holds both the base `FileSystem` and a tracing wrapper; `operator->()` and `get()` choose between them dynamically.
- `FSSequentialFileTracingWrapper`, `FSRandomAccessFileTracingWrapper`, `FSWritableFileTracingWrapper`, and `FSRandomRWFileTracingWrapper` own/wrap underlying file objects and override trace-worthy methods.
- `FSSequentialFilePtr`, `FSRandomAccessFilePtr`, `FSWritableFilePtr`, and `FSRandomRWFilePtr` provide dynamic dispatch between the tracing wrapper and the raw target.
- `FSRandomAccessFileTracingWrapper::ReadAsyncCallbackInfo` stores callback, callback arg, start time, and file operation name for async completion tracing.

## Control Flow
Construction captures the underlying object, the shared tracer, a `SystemClock` pointer, and usually the basename of the file. Pointer adapter access checks `io_tracer_ && io_tracer_->is_tracing_enabled()` on every access. If enabled, callers operate through the tracing wrapper; otherwise they operate directly on `target()`. Writable pointers own the wrapper via `unique_ptr` and expose a `reset()` method because writable file lifetime is often explicitly cleared.

## State and Persistence
All state is in-memory. The wrappers retain `shared_ptr<IOTracer>`, so a tracer stays alive while wrappers exist. File wrappers keep only basename strings, not full paths. No durable data is written by the header itself; durable trace output is produced by the `.cc` implementation through `IOTracer`.

## Dependencies and Integration Points
Depends on `rocksdb/file_system.h`, `rocksdb/system_clock.h`, and `trace_replay/io_tracer.h`. These wrappers integrate with RocksDB environments that need I/O trace capture without replacing the underlying storage engine. They rely on wrapper base classes such as `FileSystemWrapper`, `FSSequentialFileOwnerWrapper`, `FSRandomAccessFileOwnerWrapper`, `FSWritableFileOwnerWrapper`, and `FSRandomRWFileOwnerWrapper`.

## Risks and Edge Cases
- Pointer adapters return raw pointers into wrapper-owned objects; users must not outlive the owning adapter.
- The enabled/disabled choice is dynamic, so the same `FileSystemPtr` or file pointer can expose different virtual dispatch targets over time if tracing is toggled.
- `FSWritableFilePtr::get()` can return `nullptr` after `reset()`, unlike the other pointer wrappers.
- Because only basenames are stored, trace consumers cannot distinguish same-named files in different directories without external context.

## Test Signals
This header has no local unit test in the listed files. Useful tests would assert disabled-mode bypass, enabled-mode wrapper routing, writable pointer reset behavior, and async callback state cleanup. Integration tests should verify trace records are emitted for all declared overrides.
