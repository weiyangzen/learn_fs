# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/locks.c

Implementation pieces for the portability layer declared in `locks.h`; most lock operations are macros in the header, while this file supplies functions that cannot be macro-only.

Key functions:
- `ub_thread_blocksigs()`: blocks all signals for the current thread or process using `pthread_sigmask`, Solaris `thr_sigsetmask`, or `sigprocmask`.
- `ub_thread_sig_unblock(int sig)`: unblocks one signal using the same platform-dependent APIs.
- No-thread fallback:
  - `ub_thr_fork_create(...)`: simulates thread creation by `fork()`, runs the function in the child, exits child with status 0.
  - `ub_thr_fork_wait(...)`: waits on the child process and logs abnormal exits.
- Solaris:
  - `ub_thread_key_get(...)`: wrapper around `thr_getspecific`.
- Windows:
  - `log_win_err(...)`: formats `GetLastError()`.
  - `lock_basic_init/destroy/lock/unlock(...)`: implements a simple interlocked spin/sleep mutex using `InterlockedExchange` and exponential `Sleep`.
  - TLS key helpers: `ub_thread_key_create`, `ub_thread_key_set`, `ub_thread_key_get`.
  - Thread helpers: `ub_thread_create`, `ub_thread_self`, `ub_thread_join`.

Dependencies:
- Includes `util/locks.h`, `signal.h`, and optionally `sys/wait.h`.
- Uses logging/fatal-exit functions through `LOCKRET`, `log_err`, `log_warn`, and `fatal_exit`.

Research notes:
- The file is highly conditional; OpenBSD/pthread builds primarily use the macro definitions in `locks.h`.
- The no-thread mode has process isolation, so comments explicitly note that no shared data structures or real locking exist in that fallback.
