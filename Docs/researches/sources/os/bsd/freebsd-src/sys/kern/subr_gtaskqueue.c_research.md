# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_gtaskqueue.c

## Purpose
Implements group taskqueues and taskqgroups, used for CPU-distributed deferred work such as softirq-style processing.

## Key Elements
- Queue object: `struct gtaskqueue`.
- Active task tracking: `struct gtaskqueue_busy`.
- Defined group: `TASKQGROUP_DEFINE(softirq, mp_ncpus, 1)`.
- Enqueue/cancel/drain: `grouptaskqueue_enqueue()`, `gtaskqueue_cancel()`, `gtaskqueue_drain()`, `gtaskqueue_drain_all()`.
- Blocking: `grouptask_block()`, `grouptask_unblock()`, `gtaskqueue_block()`, `gtaskqueue_unblock()`.
- Worker loop: `gtaskqueue_thread_loop()`, `gtaskqueue_run_locked()`.
- Taskqgroup APIs: `taskqgroup_create()`, `taskqgroup_attach()`, `taskqgroup_attach_cpu()`, `taskqgroup_detach()`, `taskqgroup_bind()`, `taskqgroup_drain_all()`.

## Behavior
A `gtaskqueue` holds pending tasks in an STAILQ and running tasks in an active list. Enqueue refuses already queued tasks or `TASK_NOENQUEUE` tasks. Workers pull tasks, clear `TASK_ENQUEUED`, record active sequence numbers, run callbacks, and wake drainers.

Drain-all uses a high-priority barrier task to wait until currently queued tasks have started, then waits for active tasks with sequence numbers from before the drain. Network tasks are run inside `NET_EPOCH` while consecutive net tasks continue.

Taskqgroups create one fast queue per selected CPU. Attach chooses the least-loaded queue, preferring one without the same uniqueness token, and optionally binds device interrupts to the queue CPU.

## Research Notes
The group placement logic balances work while avoiding multiple queues for the same uniqueness key when possible. The queue worker can switch in and out of net epoch mode based on task flags.
