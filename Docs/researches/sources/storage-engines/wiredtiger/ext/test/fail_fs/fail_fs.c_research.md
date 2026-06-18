# sources/storage-engines/wiredtiger/ext/test/fail_fs/fail_fs.c

## Purpose
This file implements a WiredTiger test file-system extension that injects read or write failures. It is intended for POSIX test environments and can fail after configured operation counts or under environment-variable control.

## Important APIs, Types, and Functions
`FAIL_FILE_SYSTEM` embeds `WT_FILE_SYSTEM`, stores a global pthread rwlock, fail counters, configuration flags, a file-handle queue, and the `WT_EXTENSION_API`. `FAIL_FILE_HANDLE` embeds `WT_FILE_HANDLE`, stores the owning filesystem and POSIX fd, and is queued for cleanup. The public vtable is filled in `wiredtiger_extension_init` and registered through `WT_CONNECTION->set_file_system`.

## Control Flow
Initialization parses `environment`, `verbose`, `allow_writes`, and `allow_reads`. Fixed allowances enable failure immediately; environment mode checks `WT_FAIL_FS_ENABLE`, `WT_FAIL_FS_READ_ALLOW`, and `WT_FAIL_FS_WRITE_ALLOW` on each read/write. Reads and writes update counters under the global lock, optionally return `EIO` via `fail_fs_simulate_fail`, then perform POSIX `pread`/`pwrite` in chunks capped at 1 GiB.

Opens translate WiredTiger flags into POSIX flags, support directory handles with fd `-1`, allocate a wrapper handle, install the handle vtable, and add it to the queue. Termination removes remaining handle structures and destroys the lock.

## State and Persistence Behavior
The extension persists data through direct POSIX filesystem operations. It does not buffer or journal data itself, and `fh_sync` is a no-op. Runtime counters and failure state are in-memory only. Directory listing is based on the open handle queue rather than scanning the underlying directory.

## Dependencies and Integration Points
The file depends on `wiredtiger_ext.h`, POSIX I/O, pthread rwlocks, `execinfo.h` for backtraces, `queue.h`, and `test_util.h`. It integrates as the connection's file-system replacement.

## Risks and Edge Cases
This is not portable to Windows. Directory handles return early from close without queue removal, relying on termination cleanup. Remove and rename return raw POSIX results. Environment parsing treats invalid values as zero. Directory listing semantics are intentionally simplified for tests.

## Test Signals
Tests should cover fixed and environment-driven failures, successful I/O before thresholds, verbose backtraces, 1 GiB chunking, queue cleanup, directory handle behavior, and registration through `set_file_system`.
