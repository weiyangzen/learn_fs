# File Research: sources/os/bsd/openbsd-src/sys/sys/task.h

Defines the OpenBSD kernel task queue interface. `struct task` contains a TAILQ link, callback, argument, flags, and an NKCOV process pointer. The only task state flag here is `TASK_ONQUEUE`.

Kernel-only declarations expose the global task queues `systq` and `systqmp`, creation/destruction, barriers, setup, enqueue, delete, and `task_pending()`. `TASKQ_MPSAFE` marks queues that can run without the big kernel lock. This is a small deferred-work API, comparable to timeouts but for queued callback execution rather than time-based scheduling.
