# sources/storage-engines/wiredtiger/src/include/os_fstream_inline.h

## Purpose
Defines inline stream helpers that dispatch through `WT_FSTREAM` function pointers and provide a durable flush-close-rename sequence for replacing files.

## Important APIs, Types, And Functions
- `__wt_getline` calls `fstr_getline`.
- `__wt_fclose` nulls the caller's stream pointer and calls `close`.
- `__wt_fflush` calls `fstr_flush`.
- `__wt_vfprintf` and `__wt_fprintf` dispatch formatted writes through `fstr_printf`.
- `__wt_sync_and_rename` flushes a stream, fsyncs its file handle, closes it, and renames a temporary file into place durably.

## Control Flow
Simple wrappers call the configured stream method. `__wt_fclose` is null-safe and clears ownership before closing. `__wt_sync_and_rename` accumulates errors with `WT_TRET` for flush/fsync/close, returns any accumulated error before rename, and only renames after the temporary file is durably closed.

## State And Persistence Behavior
Stream operations mutate stream offsets/buffers and underlying file contents. `__wt_sync_and_rename` is a persistence-critical sequence used for atomic-ish replacement of metadata/config-style files: write temp, flush, fsync, close, durable rename.

## Dependencies And Integration Points
Depends on `WT_FSTREAM` vtables, `__wt_fsync`, `__wt_fs_rename`, error accumulation macros, and formatted-output attributes. Integrated with metadata/turtle/config file writing and other text/binary stream users.

## Risks
Clearing `*fstrp` before close prevents double close but requires callers not to reuse the pointer after error. Rename is skipped if flush/fsync/close fails. Correct durability depends on filesystem implementation of fsync and durable rename.

## Test Signals
Tests should cover null close, method error propagation, formatted write variadics, flush/fsync/close error precedence, successful durable temp-file replacement, and filesystem extensions with custom stream implementations.
