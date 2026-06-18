# sources/storage-engines/foundationdb/fdbrpc/libeio/xthread.h

## Purpose

`xthread.h` abstracts thread, mutex, condition variable, signal-mask, and result-pipe operations for libeio across Windows and POSIX platforms. It lets `eio.c` use one set of `X_*` macros for worker-thread management.

## Important APIs, types, and functions

The file defines `xmutex_t`, `xcond_t`, `xthread_t`, `X_MUTEX_INIT`, `X_MUTEX_CREATE`, `X_LOCK`, `X_UNLOCK`, `X_COND_INIT`, `X_COND_CREATE`, `X_COND_SIGNAL`, `X_COND_WAIT`, `X_COND_TIMEDWAIT`, `X_THREAD_PROC`, `X_THREAD_ATFORK`, `thread_create()`, and `respipe_read`/`respipe_write`/`respipe_close`. POSIX builds optionally use adaptive mutexes on Linux and create detached pthreads with signals blocked during `pthread_create()`.

## Control flow, state, and persistence

`thread_create()` initializes detached thread attributes, blocks all signals around pthread creation on POSIX so workers do not inherit signal delivery, creates the thread, restores the old signal mask, and destroys attributes. On Windows it uses pthread-compatible wrappers and socket-style result pipe functions. It holds no persistent state beyond objects owned by callers.

## Dependencies and integration points

`eio.c` includes this header after optionally mapping `EIO_STACKSIZE` to `X_STACKSIZE`. The file depends on pthread headers for both POSIX and the Windows compatibility path in this vendored copy, plus WinSock/Windows headers for `_WIN32`.

## Risks and test signals

The POSIX code comments out explicit stack-size setting to avoid jemalloc-related stack overflow, so worker stacks use platform defaults. Signal masking around worker creation is important for FoundationDB processes that manage signals centrally; regressions could deliver signals on I/O workers. Test with libeio worker startup/shutdown, signal-handling tests, and high-concurrency AsyncFileEIO workloads.
