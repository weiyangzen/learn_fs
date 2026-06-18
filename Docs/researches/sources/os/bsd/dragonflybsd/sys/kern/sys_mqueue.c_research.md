# File Research: sources/os/bsd/dragonflybsd/sys/kern/sys_mqueue.c

## Summary
Implements POSIX message queues as descriptor-backed kernel objects. Queues live in a global named list, are opened through normal file descriptors, support priority-ordered messages, timed send/receive, notification, attributes, unlink semantics, and kqueue readiness.

## Main Responsibilities
- Initializes the global queue-list lock in `mqueue_sysinit()`.
- Maintains system tunables/sysctls for maximum descriptors, priorities, message size, default message count, and maximum message count.
- Implements queue creation/opening in `sys_mq_open()` with permission checks and descriptor allocation.
- Implements descriptor close through `mq_close_fop()` and unlink through `sys_mq_unlink()`.
- Implements receive paths `sys_mq_receive()` and `sys_mq_timedreceive()` via `mq_receive1()`.
- Implements send paths `sys_mq_send()` and `sys_mq_timedsend()` via `mq_send1()`.
- Implements `mq_notify`, `mq_getattr`, `mq_setattr`, stat, and kqueue filters.

## Important Behavior
The global list and per-process `p_mqueue_cnt` are protected by `mqlist_mtx`; individual queue state is protected by `mq_mtx`, with lock order `mqlist_mtx -> mq_mtx`.

Priorities below `MQ_PQSIZE` are mapped into fixed priority buckets tracked by a bitmap. Higher priorities go into a reserved sorted queue (`MQ_PQRESQ`) so runtime increases to `mq_prio_max` can still work. Receivers pull from the reserved queue first, then from the highest-priority bitmap bucket.

Blocking receive sleeps on `mq_send_cv`; blocking send sleeps on `mq_recv_cv`. Timed operations convert absolute timespecs to ticks with `abstimeout2timo()`. Unlink marks `MQ_UNLINK`, wakes waiters, notifies kqueue listeners, and destroys the queue immediately only when the reference count is zero; otherwise the last close destroys it.

## Dependencies and Integration
The implementation uses DragonFly file descriptors (`falloc`, `fsetfd`, `fdrop`, `sys_close`), `struct fileops`, kqueue filters, `vaccess`, process credentials, signals, and sysctl. Message queues are typed as `DTYPE_MQUEUE` and are not vnode-backed despite exposing `fo_stat`.

## Risks
The source comments explicitly note POSIX violations where queue state is changed before user copyout in receive and setattr paths. Notification is mostly signal-based; richer `sigevent` payload setup is commented out. Queue nonblocking state is stored in shared queue attributes, so it affects all descriptors for the queue rather than only one open file description.
