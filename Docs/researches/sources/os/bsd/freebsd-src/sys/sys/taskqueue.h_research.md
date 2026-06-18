# File Research: sources/os/bsd/freebsd-src/sys/sys/taskqueue.h

## Scope

This kernel-only header declares FreeBSD taskqueue APIs: deferred task queues, timeout tasks, thread-backed queues, software-interrupt queues, fast-interrupt-compatible queues, callbacks, and global taskqueue declaration/definition macros.

## APIs And Constants

- Defines taskqueue callback types `TASKQUEUE_CALLBACK_TYPE_INIT` and `TASKQUEUE_CALLBACK_TYPE_SHUTDOWN`, plus callback count/name length constants.
- Defines enqueue flags `TASKQUEUE_FAIL_IF_PENDING` and `TASKQUEUE_FAIL_IF_CANCELING`.
- Declares `taskqueue_callback_fn` and `taskqueue_enqueue_fn`.
- Declares queue lifecycle APIs: `taskqueue_create()`, `taskqueue_create_fast()`, start-thread variants, `taskqueue_free()`, `taskqueue_block()`, `taskqueue_unblock()`, and callback registration.
- Declares task operations: enqueue, enqueue with flags, enqueue timeout by ticks or sbt, poll busy, cancel, cancel timeout, drain task, drain timeout, drain all, quiesce, run, and membership checks.
- Provides `TASK_INITIALIZER`, `TASK_INIT_FLAGS`, `TASK_INIT`, and `TIMEOUT_TASK_INIT`.
- Provides global queue macros `TASKQUEUE_DECLARE`, `TASKQUEUE_DEFINE`, `TASKQUEUE_DEFINE_THREAD`, `TASKQUEUE_FAST_DEFINE`, and `TASKQUEUE_FAST_DEFINE_THREAD`.
- Declares standard global queues: `taskqueue_swi_giant`, `taskqueue_swi`, `taskqueue_thread`, `taskqueue_fast`, and `taskqueue_bus`.

## Control Flow And Integration

- A taskqueue is created with an enqueue callback that schedules execution, commonly by waking a kernel thread or scheduling software interrupt processing.
- Thread-backed queues use `taskqueue_thread_enqueue()` and `taskqueue_thread_loop()`.
- `TASKQUEUE_DEFINE*` macros create global queue pointers and register SYSINIT initialization at taskqueue subsystem order.
- Fast taskqueues use spin-compatible locking and are intended for contexts where sleep mutexes are not legal.
- Timeout tasks bind a callout-style delayed trigger to a taskqueue.

## Dependencies

- Kernel-only; emits a preprocessor error outside `_KERNEL`.
- Depends on queue primitives, task definitions from `<sys/_task.h>`, cpuset types, kernel threads/processes, SYSINIT, priority constants, and callout/sbt timing types.

## Risks And Invariants

- Task priority is stored in 8 bits; `TIMEOUT_TASK_INIT` statically enforces priority range 0 through 255.
- Callers must drain or cancel tasks before freeing backing storage to avoid use-after-free.
- Fast queues must only use primitives legal in fast interrupt context.
- `TASKQUEUE_FAIL_IF_PENDING` and canceling flags alter enqueue semantics and must be chosen with races in mind.
