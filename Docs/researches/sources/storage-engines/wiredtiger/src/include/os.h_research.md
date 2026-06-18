# sources/storage-engines/wiredtiger/src/include/os.h

## Purpose
Defines generic OS abstraction helpers for syscall error normalization/retry, time-difference conversion, file-handle queue management, platform-specific file handle layouts, in-memory file handles, and stream abstraction state.

## Important APIs, Types, And Functions
- `WT_SYSCALL` normalizes syscall return conventions into WiredTiger error codes.
- `WT_SYSCALL_RETRY` retries transient filesystem/resource errors up to `WT_RETRY_MAX`.
- `WT_TIMEDIFF_*` and `WT_CLOCKDIFF_*` convert `timespec` or WiredTiger clock deltas.
- `WT_FILE_HANDLE_INSERT` and `WT_FILE_HANDLE_REMOVE` maintain both global and hash file-handle queues.
- `struct __wt_fh` is the internal wrapper for a `WT_FILE_HANDLE`, with name, hash, sync/write accounting, queues, refcount, and file type.
- `struct __wt_file_handle_win`, `struct __wt_file_handle_posix`, and `struct __wt_file_handle_inmem` hold platform/in-memory handle specifics.
- `struct __wt_fstream` wraps stream state and function pointers for close, flush, getline, and printf.

## Control Flow
Syscall wrappers inspect return values, convert `-1` through `errno`, and retry selected transient errors with a short sleep. Queue macros insert/remove a file handle from two TAILQ lists in a single operation. Stream functions are implemented in `os_fstream_inline.h` by dispatching through `WT_FSTREAM` function pointers.

## State And Persistence Behavior
File handle structures represent open persistent files or in-memory files. `written` and `last_sync` track runtime durability state. POSIX mmap fields track memory-mapped file state and resizing/use counts. Stream state includes offsets, size, buffer, mode flags, and underlying `WT_FH`.

## Dependencies And Integration Points
Depends on queue macros, filesystem extension interfaces (`WT_FILE_HANDLE`, `WT_FILE_SYSTEM`), platform OS typedefs, error handling, and timing constants. Used by all filesystem, block manager, metadata, log, backup, and stream code.

## Risks
Queue insert/remove must keep both lists consistent. Retry policy can hide transient errors briefly but must not retry non-transient failures. POSIX mmap resizing and use counts are concurrency-sensitive. File handle name duplication requires consistent ownership. Stream flags and function pointers must match how a stream was opened.

## Test Signals
Signals include syscall retry tests with injected `EINTR`/`EAGAIN`/`ENOSPC`, file-handle queue consistency checks, POSIX mmap resize stress, Windows/POSIX handle lifecycle tests, in-memory filesystem tests, stream mode tests, and durability accounting around `written`/`last_sync`.
