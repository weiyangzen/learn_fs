# sources/storage-engines/wiredtiger/test/windows/windows_shim.h

## Purpose
`windows_shim.h` declares the Windows compatibility surface for WiredTiger tests. It supplies missing constants, aliases, POSIX-like structs, type definitions, function prototypes, and macro mappings so Unix-oriented test code can compile under MSVC.

## Important APIs and types
The header defines `R_OK`, `X_OK`, `strcasecmp`, `PATH_MAX`, `mkdir`, `S_ISDIR`, `struct timeval`, `pid_t`, `glob_t`, `useconds_t`, pthread-like mutex/condition/rwlock/thread typedefs, and wrappers for `lseek`, `read`, and `write`. It declares `gettimeofday`, `glob`, `globfree`, `sleep`, `usleep`, pthread creation/join/rwlock functions, and `last_windows_error_message`.

## Control flow and behavior
There is no runtime control flow in the header. Its behavior is compile-time adaptation: older MSVC versions map `snprintf` to `__wt_snprintf`, `_mkdir` backs `mkdir`, `_read`/`_write`/`_lseek` back POSIX names, and the `rwlock_wrapper` embeds an `SRWLOCK` plus an exclusive-owner marker.

## State, dependencies, and integration
The header includes `wt_internal.h`, `<sys/utime.h>`, and `<direct.h>`, and is included by `test_util.h` only under `_WIN32`. It is paired with the `windows_shim` static library from the Windows CMake file.

## Risks and test signals
Risks include semantic gaps from POSIX emulation, especially pthread behavior and filesystem mode handling. Macro remapping can also hide portability problems if code depends on Unix-only semantics. Signals include clean Windows compilation, tests resolving all declared shim symbols, correct include visibility from CMake, and no conflicting declarations with MSVC or Windows SDK headers.
