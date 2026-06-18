# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sleepq.c

Implements sleep queue operations for kernel threads waiting on synchronization objects or wait channels.

Core structure:
- Global `sleepq_head[NSLEEPQ]` stores sleep queue buckets.
- Each sleep queue is a singly linked list in descending dispatch priority order.
- Threads of the same priority form circular doubly linked sublists via `t_priforw` and `t_priback`.
- The main chain uses `t_link`; membership is recorded in `t_sleepq`.

Important paths:
- `sleepq_insert()` inserts a thread in priority order. For `lwp_rwlock_t`, writers are treated as a half-priority higher than readers through `CMP_PRIO()`.
- `sleepq_unlink()` removes a thread from both the main list and the priority sublist, then clears all queue linkage fields.
- `sleepq_dequeue()` removes a specific thread without waking it.
- `sleepq_unsleep()` removes a sleeping thread and transitions it toward runnable state.
- `sleepq_wakeone_chan()` wakes the first thread waiting on a specific channel, marks `TS_SIGNALLED`, calls class wakeup, and drops the run queue lock.
- `sleepq_wakeall_chan()` wakes all threads waiting on a channel.

Locking and invariants:
- Callers must hold the appropriate thread/sleepq lock; assertions check `THREAD_LOCK_HELD`.
- Removal is optimized by using `t_sleepq` and priority-sublist backlinks rather than full-list scans in the common case.
- Wake functions clear `t_wchan`, `t_wchan0`, and `t_sobj_ops` before calling scheduler-class wakeup hooks.

Filesystem relevance:
- Sleep queues are core blocking/wakeup infrastructure. Filesystems, VFS, drivers, and VM code rely on this machinery indirectly through condition variables, locks, and wait channels.
