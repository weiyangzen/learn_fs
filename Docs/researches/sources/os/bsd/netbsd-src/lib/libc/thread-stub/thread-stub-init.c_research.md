# File Research: sources/os/bsd/netbsd-src/lib/libc/thread-stub/thread-stub-init.c

## Purpose
Provides weak thread initialization and errno hooks when `_REENTRANT` is enabled but libpthread is absent.

## Key Elements
Defines weak `__libc_thr_init` as a no-op startup function and weak `__libc_thr_errno` as a stub that raises `SIGABRT`.

## Dependencies
Uses `reentrant.h`, `<signal.h>`, weak aliases, and `_REENTRANT`.

## Behavior/Risks
Calling the errno thread hook without libpthread aborts deliberately, preventing silent misuse of thread-specific errno machinery.
