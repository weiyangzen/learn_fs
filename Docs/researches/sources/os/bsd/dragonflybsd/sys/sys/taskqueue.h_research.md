# File Research: sources/os/bsd/dragonflybsd/sys/sys/taskqueue.h

Kernel deferred task queue API.

Key contents:
- Defines task callback type `task_fn_t(context, pending)`.
- Defines enqueue notification callback type.
- Defines `struct task`:
  - queue linkage
  - current queue
  - pending count
  - priority
  - handler
  - context
- Defines `struct timeout_task`, combining a `task`, `callout`, and flag.
- Declares queue creation, thread startup, enqueue, cancel, drain, lookup, free, block, and unblock APIs.
- Provides initializer macros:
  - `TASK_INITIALIZER`
  - `TASK_INIT`
  - `TIMEOUT_TASK_INIT`
- Provides declaration/definition macros:
  - `TASKQUEUE_DECLARE`
  - `TASKQUEUE_DEFINE`
  - `TASKQUEUE_DEFINE_THREAD`
- Declares common queues:
  - `taskqueue_swi`
  - `taskqueue_swi_mp`
  - per-CPU `taskqueue_thread[]`

Important behavior:
- `pending` tells a task handler how many enqueue attempts accumulated before execution.
- `TASKQUEUE_DEFINE` creates the queue during `SYSINIT` at `SI_SUB_PRE_DRIVERS`.
- Thread-backed queues use `taskqueue_thread_enqueue` and daemon priority.

Research notes:
- This is FreeBSD-derived deferred execution infrastructure adapted for DragonFly priorities and per-CPU queues.
