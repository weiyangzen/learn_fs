# sources/storage-engines/rocksdb/file/read_write_util.cc

## Purpose

`read_write_util.cc` implements small filesystem utility functions used by RocksDB file readers/writers. It wraps writable-file creation for test instrumentation, implements robust file-size discovery from an open file or path fallback, and provides a debug-only sector-alignment predicate.

## Important APIs, Types, and Functions

- `NewWritableFile(...)` calls `FileSystem::NewWritableFile` with test sync-point exposure of `FileOptions.temperature` and random kill injection.
- `GetFileSizeFromOpenFileOrPath(...)` first asks an already-open `FSRandomAccessFile` for size, then optionally falls back to `FileSystem::GetFileSize`.
- `IsFileSectorAligned(...)` returns whether an offset is a multiple of sector/alignment size in debug builds.

## Control Flow and State

`NewWritableFile` is a straight wrapper: expose temperature via sync point, create file, inject a test kill point, and return status.

`GetFileSizeFromOpenFileOrPath` asserts non-null inputs, calls `file->GetFileSize`, and returns immediately on success. If the open-file size call fails with `NotSupported`, or if the caller selected `FileSizeFallback::kAnyOpenFileError`, it invokes the optional `before_path_fallback` callback and asks the filesystem for the path size. Otherwise it returns the original open-file error.

There is no persistent state. Side effects are file creation and optional test process termination through kill hooks.

## Dependencies and Integration Points

The implementation depends on `read_write_util.h`, assertions, sync points, `FileSystem`, `FSRandomAccessFile`, and `IOOptions`. `readahead_raf.cc` uses the debug alignment helper. File creation wrappers are used by code paths that need RocksDB test hooks around writable files.

## Risks and Edge Cases

- The fallback callback runs only when path fallback will be attempted; callers can use it for synchronization or instrumentation.
- Falling back on any open-file error can hide real open-handle failures if used too broadly.
- Debug-only alignment assertions disappear in release builds.

## Test Signals

Sync points and kill hooks support fault-injection tests. The alignment helper is asserted in `readahead_raf.cc` buffer reads under debug builds.
