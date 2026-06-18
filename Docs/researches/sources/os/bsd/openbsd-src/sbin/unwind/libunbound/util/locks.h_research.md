# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/locks.h

Portable locking and thread abstraction header for Unbound.

Key contents:
- Defines `LOCKRET(func)` unless provided by the includer. It logs nonzero pthread/Solaris-style return codes.
- Supports optional lock-debug mode through `USE_THREAD_DEBUG`, enabled when pthreads, spinlocks, and `ENABLE_LOCK_CHECKS` are present.
- Defines three lock classes:
  - `lock_rw_type`: reader/writer lock, falling back to mutex if rwlocks are unavailable.
  - `lock_basic_type`: ordinary mutex.
  - `lock_quick_type`: spinlock where available, otherwise mutex.
- Defines thread abstraction:
  - pthread: `pthread_t`, `pthread_create`, `pthread_join`, `pthread_key_t`, thread naming variants, and a wrapper that raises stack size to at least 2 MiB.
  - Solaris threads: `thread_t`, `thr_create`, `thr_join`, TLS wrappers.
  - Windows threads: `HANDLE` threads, `DWORD` TLS keys, lock routines implemented in `locks.c`.
  - no threads: `THREADS_DISABLED`, no-op locks, fork-based thread simulation, pid-based self/join.
- Declares:
  - `ub_thread_blocksigs()`
  - `ub_thread_sig_unblock(int sig)`

Important behavior:
- `PTHREADSTACKSIZE` is fixed at `2*1024*1024` to avoid small default stacks on musl/Alpine.
- Thread naming is handled through multiple platform-specific `pthread_setname_np` variants when detected.
- In no-thread mode, locks are all no-ops and `ub_thread_create` maps to fork simulation.

Research notes:
- This header is a portability foundation for logging, networking, caches, and OpenSSL lock callbacks.
- Most users include this file for macros, so changing it has broad compile-time impact.
