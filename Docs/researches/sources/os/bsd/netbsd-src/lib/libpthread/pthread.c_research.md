# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread.c

## Purpose
Core NetBSD pthread runtime implementation: initialization, thread creation/exit/join, cancellation, thread identity, diagnostics, park/unpark, fork handling, stack setup, and global thread tracking.

## Main Responsibilities
- Initializes libpthread state in `pthread__init()`: TSD storage, libc threading switch, page/CPU/guard sizes, locks, queues, all-thread tree, main thread, LWP control, MD init, diagnostic options, and atfork handlers.
- Implements `pthread_create()` using stack allocation/reuse, TLS allocation, thread struct initialization, and `pthread__makelwp()`.
- Implements `pthread_exit()`, cleanup handler execution, C++ thread atexit execution, TSD destruction, malloc cleanup, zombie/dead state transitions, and LWP exit.
- Implements `pthread_join()`, `pthread_detach()`, `pthread_equal()`, `pthread_self()`, `pthread_main_np()`.
- Implements thread naming via `pthread_getname_np()` and `pthread_setname_np()`.
- Implements cancellation: `pthread_cancel`, cancel state/type setters, `pthread_testcancel`, and internal cancellation transition helpers.
- Maintains global all-thread rb-tree for validation/search and dead-thread queue for reuse.
- Provides internal assertion/error reporting avoiding lock-taking stdio paths.
- Implements `_lwp_park` / `_lwp_unpark` wrappers for pthread blocking queues.
- Initializes main thread stack from auxinfo and stack resource limits.
- Provides lock hash selection and scheduling priority validation.

## Key Implementation Notes
- Strong aliases connect libc thread stubs to real pthread functions once libpthread is linked.
- Static library binder references force inclusion of key pthread object files.
- `pthread_create()` primes `_lwp_park` before first created thread to avoid lazy rtld symbol-resolution consuming a wakeup intended for libpthread.
- Dead thread structures may be reused only after `_lwp_kill(lid, 0)` confirms the LWP no longer exists.
- Cancellation state is maintained with atomics and release/acquire barriers: `pthread_cancel()` publishes cancellation, cancellation tests acquire only on the slow path.
- `pthread__find()` uses the all-thread rb-tree to validate pthread handles and avoid accepting dead thread ids.
- `pthread__getenv()` scans `environ` directly to avoid calling lock-using `getenv()` during early pthread initialization.

## Dependencies
- NetBSD LWP syscalls and LWP control.
- TLS/rtld hooks, libc private threading stubs, atomic namespace headers.
- `pthread_int.h`, `pthread_makelwp.h`, `reentrant.h`, machine-dependent pthread macros.
