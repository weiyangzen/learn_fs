# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_gtaskqueue.c

## Summary
Implements group taskqueues and taskqgroups, a FreeBSD-compatible task execution facility used for grouped per-CPU/softirq work.

## Main Responsibilities
- Creates and runs `gtaskqueue` instances with queued and active task tracking.
- Supports enqueue, cancel, drain, block/unblock, and thread startup.
- Implements `grouptask_block()` / `grouptask_unblock()` around `TASK_NOENQUEUE`.
- Implements `taskqgroup_create()`, attach/detach, CPU-specific attach, CPU binding tasks, and drain-all behavior.
- Defines `TASKQGROUP_DEFINE(softirq, ncpus, 1)`.

## Important Behavior
Queue execution tracks active tasks through `gtaskqueue_busy` records with sequence numbers, enabling drain operations to distinguish already-running tasks from later work. `gtaskqueue_drain_tq_queue()` inserts a high-priority barrier task. Taskqgroups distribute tasks by least-loaded queue while avoiding duplicate `uniq` identifiers on a queue when possible.

## Risks
`gtaskqueue_free()` is marked unused, and `taskqgroup_destroy()` is empty, so lifecycle ownership is limited. Interrupt CPU binding code is disabled with `#if 0`. Detach blocks and drains the grouptask before removal; callers must not enqueue after detach.
