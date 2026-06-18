# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/synch.h

`synch.h` defines low-level user synchronization object layouts shared by threads, LWPs, and pthread ABI structures. It avoids pulling POSIX namespace pollution into `pthread.h`, so the comments require these layouts to stay synchronized with corresponding pthread types elsewhere.

`lwp_mutex_t` stores flag words, ceiling, type/recursive count union, magic value, owner/lock word in 32-bit or 64-bit-compatible form, and optional data. `lwp_cond_t` stores flags, type, magic, and data. `lwp_sema_t` stores count, type, magic, flags, and data. `lwp_rwlock_t` stores reader state, type, magic, and embedded mutex/condition variables used for process-shared rwlocks and ownership indication.

Synchronization type constants distinguish process-private and process-shared objects (`USYNC_THREAD`, `USYNC_PROCESS`) and lock types/attributes (`LOCK_NORMAL`, `LOCK_SHARED`, `LOCK_ERRORCHECK`, `LOCK_RECURSIVE`, `LOCK_PRIO_INHERIT`, `LOCK_PRIO_PROTECT`, `LOCK_ROBUST`). `USYNC_PROCESS_ROBUST` is a deprecated historical alias mapped by initialization code. Mutex flags describe owner-dead, not-recoverable, initialized, unmapped, and deadlock states.
