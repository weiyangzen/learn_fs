# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/windows_io.c

## Purpose
Windows implementation of the libext2fs I/O manager using Win32 handles and a small block cache.

## Main Behavior
- Opens devices through `CreateFile`, with fake DOS device aliases for raw NT-style names that need `\\.\...` access.
- Wraps the handle with `_open_osfhandle` for stat/close compatibility.
- Implements raw block reads/writes using `SetFilePointerEx`, `ReadFile`, and `WriteFile`.
- Uses bounce buffers for unaligned or forced-buffered I/O.
- Maintains an 8-entry dirty block cache similar to the Unix manager.
- Supports blocksize changes by flushing and reallocating cache buffers.

## Supported Operations
- Reads, writes, flush, stats, and `offset` option.
- `zeroout` can extend regular files but ultimately reports unimplemented for actual zeroing.
- Readahead, byte writes, discard, and block-device zeroout are not supported.

## Integration
Exports `windows_io_manager` and Windows versions of `ext2fs_open_file`, `ext2fs_stat`, and `ext2fs_fstat`.

## Risks / Notes
- Error values come from `GetLastError()` in raw Win32 paths and `errno` in C runtime paths.
- Fake DOS device cleanup is required on close/open failure.
- The Windows manager is less feature-complete than Unix, especially for discard/zeroout.
