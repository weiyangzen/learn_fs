# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iso/signal_iso.h

## Role

`signal_iso.h` provides the ISO C/POSIX-visible signal-number and signal-handler macro subset included indirectly through public Sun/illumos signal headers. It is intentionally limited to standard identifiers and compatibility aliases.

## Major Definitions

The file defines traditional UNIX signal numbers from `SIGHUP` through `SIGINFO`, including aliases such as `SIGABRT`/`SIGIOT`, `SIGCHLD`/`SIGCLD`, and `SIGIO`/`SIGPOLL`. It reserves real-time signal bounds as `_SIGRTMIN` 42 and `_SIGRTMAX` 73, while public `SIGRTMIN` and `SIGRTMAX` are computed dynamically through private `_sysconf(_SC_SIGRT_MIN/MAX)`.

Signal action macros are C++-, lint-, and C-specific forms of `SIG_DFL`, `SIG_ERR`, `SIG_IGN`, and `SIG_HOLD`. For C++, the file introduces `SIG_FUNC_TYP`, `SIG_TYP`, and `SIG_PF` to type signal handlers. It also defines `SIG_BLOCK`, `SIG_UNBLOCK`, and `SIG_SETMASK` values for signal-mask operations.

## Interfaces

The only function declaration is private `_sysconf(int)`, used by the real-time signal macros. The rest of the file is macro/type definition.

## Integration Notes

This header is a public ABI surface. Signal numbers and handler sentinel values are not ordinary internal constants; changing them would break applications, libc behavior, and kernel/user signal semantics. New standard signal identifiers are expected to be added here and coordinated with `<sys/signal.h>` namespace handling.
