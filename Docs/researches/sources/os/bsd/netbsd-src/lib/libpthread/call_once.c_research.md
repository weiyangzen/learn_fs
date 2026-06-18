# File Research: sources/os/bsd/netbsd-src/lib/libpthread/call_once.c

## Purpose
Implements the C11 `call_once()` API on top of POSIX pthread once control.

## Main Responsibilities
- Validates non-null arguments with `_DIAGASSERT`.
- Calls `pthread_once(flag, func)`.
- Ignores the pthread return value because C11 `call_once` returns `void`.

## Dependencies
- `pthread.h`, `threads.h`.
