# File Research: sources/os/plan9/plan9/sys/src/9/port/qlock.c

Implements sleepable queued locks and reader/writer locks.

QLock:
- `qlock` acquires immediately if unlocked, otherwise enqueues `up` on FIFO wait queue and schedules away.
- `canqlock` attempts nonblocking acquisition.
- `qunlock` wakes the next queued process or clears the locked state.
- Tracks holder PC in `qpc` for diagnostics.

RWlock:
- `rlock` grants readers when no writer and no waiting queue; otherwise queues as `QueueingR`.
- `runlock` decrements readers and wakes a waiting writer when the last reader exits.
- `wlock` grants writer when no readers/writer; otherwise queues as `QueueingW`.
- `wunlock` prefers a queued writer; otherwise wakes all leading queued readers.
- `canrlock` is a nonblocking reader acquisition that fails if any writer is active or queued.

Diagnostics:
- `rwstats` counts lock acquisitions and queueing.
- `qlock` warns if called while interrupt locks or spin locks are held.

Role:
- Sleepable synchronization primitive used throughout process, namespace, queue, and VM code.
