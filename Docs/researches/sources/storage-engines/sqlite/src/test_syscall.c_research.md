<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_syscall.c -->
# sources/storage-engines/sqlite/src/test_syscall.c

## Purpose
`test_syscall.c` provides Tcl-controlled fault injection for Unix VFS system calls. It tests error handling in `os_unix.c` by installing wrapper functions through VFS `xSetSystemCall()` and configuring transient or persistent failures.

## Important APIs, Types, And Functions
The global `gSyscall` stores failure countdown, persistence, failure count, fake page size, and original `getpagesize`. `aSyscall[]` maps syscall names to wrapper pointers, original pointers, and errno defaults. Wrappers include `ts_open()`, `ts_close()`, `ts_ftruncate()`, `ts_fcntl()`, `ts_read()`, `ts_pread()`, `ts_write()`, `ts_pwrite()`, `ts_fallocate()`, `ts_mmap()`, and `ts_mremap()`. Tcl subcommands are implemented by `test_syscall_install()`, `uninstall`, `reset`, `fault`, `errno`, `exists`, `list`, `defaultvfs`, and `pagesize`.

## Control Flow
Tests install selected wrappers by saving the original syscall pointer from the default VFS and replacing it. Each wrapper calls `tsIsFail()` or `tsIsFailErrno()` to decrement the countdown and decide whether to fail. `fault COUNT PERSIST` configures when failure starts and whether all later wrapped calls fail. `errno CALL ERRNO` changes the error reported by a wrapper. Reset/uninstall restore original calls individually or through the VFS reset hook. Page-size testing replaces `getpagesize` with a wrapper returning a configured power-of-two size.

## State And Persistence Behavior
All state is process-local and only active on Unix builds. Installed wrappers mutate the default VFS syscall table until reset. The close wrapper deliberately closes the real file descriptor even when simulating an error to avoid descriptor leaks during long tests.

## Dependencies And Integration Points
The file is compiled meaningfully only when `SQLITE_OS_UNIX` is true and the VFS supports version 3 syscall hooks. It depends on Tcl, errno names, Unix system headers, and SQLite's `sqlite3_syscall_ptr` interface.

## Risks And Test Signals
Risks include global process-wide effects, varargs wrapper mismatches, platform-specific syscall availability, default errno values of zero for some wrappers, and failure countdowns consumed by unexpected internal calls. Test signals include install/list/exists matching VFS support, deterministic one-shot and persistent failures, expected SQLite error codes for each injected errno, `EINTR` write partial-write simulation, page-size override behavior, and full reset restoring normal VFS operation.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_syscall.c -->
