# File Research: sources/os/bsd/freebsd-src/sys/sys/_task.h

Taskqueue task structure definitions.

Key elements:
- Defines `task_fn_t` and `struct task` with queue link, pending count, priority, flags, handler, and context.
- Defines task flags for enqueued, no-enqueue, and network tasks.
- Defines `struct timeout_task`.
- Under `_KERNEL`, defines `gtask_fn_t` and `struct gtask`.

Dependencies:
- Includes `sys/_callout.h` and `sys/queue.h`.

Research notes:
- Taskqueues are deferred execution infrastructure used throughout drivers, storage, networking, and filesystem-adjacent code.
