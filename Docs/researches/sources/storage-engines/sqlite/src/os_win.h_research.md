# sources/storage-engines/sqlite/src/os_win.h

## Purpose

`os_win.h` is the small platform header shared by SQLite's Windows-specific source files. It centralizes inclusion of the Windows SDK header, adds Cygwin POSIX compatibility headers, and defines the `SQLITE_OS_WIN_THREADS` feature macro used by the Windows thread implementation.

The header is guarded by `SQLITE_OS_WIN_H` and is only meaningful for SQLite builds that may compile Windows support. It does not declare the full Windows VFS API; most helpers in `os_win.c` are static or declared ad hoc by direct consumers.

## Important APIs, Types, And Functions

- `#include "windows.h"` imports Win32 types and APIs such as `HANDLE`, `DWORD`, `BOOL`, `LPWSTR`, `LPCWSTR`, `FILETIME`, `SYSTEM_INFO`, and thread primitives used throughout `os_win.c`, `mutex_w32.c`, `threads.c`, and test files.
- Under `__CYGWIN__`, the header includes `<sys/cygwin.h>`, `<sys/stat.h>`, `<unistd.h>`, and `<errno.h>` so the Windows VFS can use Cygwin path conversion, `lstat()`, `readlink()`, `getcwd()`, and `errno` integration.
- `SQLITE_OS_WIN_THREADS` is defined to `1` only when all of these hold: `SQLITE_OS_WIN` is true, `SQLITE_THREADSAFE>0`, and the build is not Cygwin. Otherwise it is `0`.

## Control Flow

This header has no runtime control flow. Its compile-time flow is:

1. Prevent duplicate inclusion with `SQLITE_OS_WIN_H`.
2. Include `windows.h`.
3. Include extra Cygwin compatibility headers only for `__CYGWIN__`.
4. Define `SQLITE_OS_WIN_THREADS` according to the platform and SQLite thread-safety macros.

## State And Persistence Behavior

`os_win.h` owns no runtime state and performs no persistence. Its effect is compile-time only: it makes platform types visible and selects whether SQLite should compile native Windows `_beginthreadex()`/`_endthreadex()` thread support. That macro changes which thread backend code is active, but the stateful behavior lives in the consuming source files.

## Dependencies And Integration Points

The header depends on the Windows SDK and, for Cygwin builds, the Cygwin/POSIX compatibility headers. It is included by `os_win.c`, `mutex_w32.c`, `threads.c`, `test_config.c`, and `test1.c`. `threads.c` also declares `sqlite3Win32Wait(HANDLE)` from `os_win.c`, and `mutex_w32.c` declares `sqlite3_win32_sleep(DWORD)` from `os_win.c`; both declarations rely on Win32 types made available here.

`SQLITE_OS_WIN_THREADS` integrates with SQLite's thread abstraction. It prevents the native Win32 thread path from being used on Cygwin and non-threadsafe builds, even when general Windows OS support is enabled.

## Risks And Edge Cases

- Including `windows.h` can affect namespace, macro, and include-order behavior across SQLite's Windows-specific compilation units. This header intentionally keeps that include localized to Windows-oriented files.
- `SQLITE_OS_WIN_THREADS` is conservative for Cygwin. Accidentally enabling native Windows thread APIs there would conflict with the Cygwin runtime expectations noted in the comment.
- The header assumes `SQLITE_OS_WIN` and `SQLITE_THREADSAFE` are already defined by SQLite configuration headers before inclusion.
- Because most `os_win.c` helper functions are not declared here, consumers use local forward declarations for cross-file helpers. Signature drift between those declarations and definitions would be caught only at compile/link time.

## Test Signals

Useful checks are mostly build-configuration checks:

- Native Windows, threadsafe builds should see `SQLITE_OS_WIN_THREADS == 1` and compile the Win32 thread path.
- Cygwin builds should see `SQLITE_OS_WIN_THREADS == 0` while still compiling the Cygwin-aware VFS path conversion code in `os_win.c`.
- Non-threadsafe Windows builds should see `SQLITE_OS_WIN_THREADS == 0`.
- `mutex_w32.c`, `threads.c`, `test_config.c`, and `test1.c` should compile cleanly after including this header, with Win32 and Cygwin types available as appropriate.
