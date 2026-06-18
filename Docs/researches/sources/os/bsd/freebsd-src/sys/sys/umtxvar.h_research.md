# File Research: sources/os/bsd/freebsd-src/sys/sys/umtxvar.h

Kernel-internal umtx/futex wait-queue and priority-inheritance state header.

Key responsibilities:
- Defines umtx key types shared by native umtx and Linux futex code, covering simple waits, condition variables, semaphores, normal/PI/PP mutexes, rwlocks, futexes, shared memory, and robust variants.
- Defines `struct umtx_key` mapping user synchronization objects to either shared VM object/offset identity or private vmspace/address identity.
- Defines sharing modes, absolute timeout state, priority-inheritance record `struct umtx_pi`, waiting-thread record `struct umtx_q`, per-key wait queue, and hash-chain structure with shared/exclusive queues, spare queues, busy/waiter state, and PI list.
- Provides key matching helper.
- Declares timeout copy/init, exec cleanup, key get/release, queue allocation/free, busy/unbusy, insert/remove, requeue, signal, sleep, PI sleep, wake, PI operations, and per-thread umtx lifecycle hooks.
- Provides default shared-queue insert/remove aliases and chain lock/unlock helpers.

Dependencies:
- Kernel-only; includes `_timespec` and depends on VM object/vmspace, proc, thread, mutex, tail/list queues, and PI priority types.

Notable risks:
- Key identity is the correctness boundary for process-shared versus private waits; mismatches can wake wrong waiters or miss wakeups.
- Priority inheritance state requires both chain locks and umtx locks in documented cases.
