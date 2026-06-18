# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_psync.c

Read status: complete.

Purpose: POSIX pthread-backed synchronization and thread implementation for Ghostscript.

Main logic:
- Defines `pt_semaphore_t` with count, mutex, and condition variable.
- `gp_semaphore_open/close/wait/signal` implement counting semaphore semantics using pthread mutex/cond.
- `gp_monitor_*` maps monitors to pthread mutexes.
- `gp_create_thread` allocates a closure containing the Ghostscript callback and data, initializes detached pthread attributes, and starts a detached thread.
- `gp_thread_begin_wrapper` copies the closure, frees it, invokes the callback, and returns `NULL`.

Filesystem/storage relevance:
- No direct filesystem behavior, but it provides concurrency primitives for runtime components that may include caches or devices.

Notable behavior:
- Error mapping is coarse: most pthread failures become `gs_error_ioerror`.
- Thread attributes are not explicitly destroyed after `pthread_create`.
