# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_mutex.c

This file implements pthread mutexes and mutex attributes. Mutex ownership is held in `ptm_owner`, using pointer low bits for recursive and priority-protect flags. Waiters are tracked with lock-free lists of stack waiter records and parked with LWP primitives, avoiding userspace spinlocks around waiter queues.

Fast-path lock is a CAS from `NULL` to `self`. The slow path handles recursive/errorcheck semantics, priority protection via `_sched_protect`, adaptive spinning while the owner is running according to `lwpctl`, enqueueing the waiter, timeout handling, and wakeup races. Unlock validates ownership, handles recursive depth, releases priority protection, clears owner state, and wakes any waiters through `pthread__mutex_wakeup`. Wakeups batch LWP ids up to `pthread__unpark_max`.

Attributes encode type, protocol, and priority ceiling in `ptma_private`. Supported mutex types are normal, errorcheck, and recursive; supported protocols are none and priority-protect, while priority-inherit returns `ENOTSUP`. Process-shared support returns `ENOSYS` if compiled.

`pthread__mutex_deferwake` lets condition variables transfer waiters onto a mutex so they are woken when the mutex owner unlocks. Risks are subtle memory ordering, stack waiter lifetime, timeout removal races, and complexity around encoded owner bits.
