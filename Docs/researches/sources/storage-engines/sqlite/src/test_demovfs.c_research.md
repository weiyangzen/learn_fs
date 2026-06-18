<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_demovfs.c -->
# sources/storage-engines/sqlite/src/test_demovfs.c

## Purpose
`test_demovfs.c` implements a minimal POSIX-like SQLite VFS named `demo`. It is both example code and a test fixture for embedded-style VFS behavior, especially rollback-journal write buffering and omission of locking, temporary files, dynamic loading, and real truncation.

## Important APIs, Types, and Functions
The core type is `DemoFile`, containing `sqlite3_file base`, a POSIX file descriptor, and optional journal write buffer fields. File methods include `demoClose`, `demoRead`, `demoWrite`, `demoTruncate`, `demoSync`, `demoFileSize`, lock no-ops, `demoFileControl`, `demoSectorSize`, and `demoDeviceCharacteristics`. VFS methods include `demoOpen`, `demoDelete`, `demoAccess`, `demoFullPathname`, dynamic-loading stubs, `demoRandomness`, `demoSleep`, and `demoCurrentTime`. `sqlite3_demovfs()` returns the static VFS, and test builds register Tcl commands `register_demovfs` and `unregister_demovfs`.

## Control Flow
`demoOpen()` rejects temporary files, allocates an 8192-byte buffer for main journal files, maps SQLite open flags to POSIX `open()` flags, initializes `DemoFile`, and installs `demoio`. `demoWrite()` coalesces sequential journal writes into the fixed buffer, flushing when full or when writes are non-contiguous; non-buffered files write directly with `lseek()` and `write()`. Reads and file-size checks flush the buffer first. `demoSync()` flushes then calls `fsync()`. Delete optionally syncs the containing directory.

## State and Persistence Behavior
Database and journal state persists through POSIX file descriptors. Journal data may remain only in `DemoFile.aBuffer` until read, file-size, sync, close, or a non-contiguous/full-buffer write forces `demoFlushBuffer()`. Locking is not implemented, so SQLite is told no reserved lock exists and multi-connection use is outside the VFS contract. `demoTruncate()` is a no-op, making journal modes requiring truncation unsuitable.

## Dependencies and Integration Points
The file uses public `sqlite3.h`, POSIX calls (`open`, `read`, `write`, `fsync`, `close`, `fstat`, `access`, `unlink`, `getcwd`, `sleep`, `usleep`, `time`), and Tcl registration in `SQLITE_TEST` Unix builds. It assumes Unix path syntax, maximum path length 512, and in-memory temp storage for correct use.

## Risks
No locking means concurrent independent connections can corrupt databases. No temp-file support and no real truncate limit supported SQLite modes. `demoRandomness()` returns OK without filling bytes, so consumers should not rely on strong randomness. `demoCurrentTime()` has second precision and 32-bit time caveats. Direct writes do not retry partial writes or EINTR. Path handling is intentionally simple and Unix-specific.

## Test Signals
Signals include successful registration/unregistration, correct operation under `vfs=demo`, fewer journal write system calls by buffering, expected failure for temp files or unsupported extension loading, hot-journal rollback behavior due to no reserved lock, and correct persistence after sync/close.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_demovfs.c -->
