# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/sigwait.c

## Purpose
Implements `sigwait` over `__sigtimedwait`.

## Key Elements
Weak-aliases `sigwait` to `_sigwait`; saves `errno`, calls `__sigtimedwait(set, NULL, NULL)`, restores original `errno`, and returns the captured error number or stores the received signal.

## Dependencies
Uses `<signal.h>`, `<errno.h>`, and internal `__sigtimedwait`.

## Behavior/Risks
Preserves POSIX `sigwait` convention: return error number directly and avoid leaving `errno` changed.
