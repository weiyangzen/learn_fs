# File Research: sources/os/bsd/netbsd-src/lib/libc/include/reentrant.h

Private libc abstraction layer for thread-aware code.

Design:
- Maps libc-internal mutex, condition variable, rwlock, TSD, thread, and once types to pthread types.
- Under `_REENTRANT`, maps operations to `__libc_*` dispatch functions, which are weak-stubbed in libc and strongly supplied by pthreads when linked.
- Under non-`_REENTRANT`, most operations compile to no-ops, while `thr_once` performs a simple one-time call using `pto_done`.

Important exports:
- `mutex_t`, `cond_t`, `rwlock_t`, `thread_key_t`, `once_t`.
- `mutex_lock`, `cond_wait`, `rwlock_*`, `thr_keycreate`, `thr_setspecific`, `thr_once`, `thr_enabled`, `thr_curcpu`.
- `FLOCKFILE`/`FUNLOCKFILE` internal stdio locking macros.

Used by files such as `gmon.c`, `arc4random.h`, and environment locking code.
