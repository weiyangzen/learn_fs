# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_task.c

Read completely: 464 lines.

Implements OpenBSD kernel task queues: deferred work items serviced by one or more kernel threads. It defines the global queues `systq` and `systqmp`, dynamic queue creation/destruction, enqueue/delete operations, barriers, worker loops, and optional WITNESS/kcov integration.

Core structures and queues:
- `struct taskq` tracks lifecycle state, running worker count, configured thread count, queue flags, name, mutex, queued `struct task` list, worker thread list, barrier accounting, and WITNESS metadata.
- `taskq_sys` is the default kernel-locked task queue; `taskq_sys_mp` is the MP-safe queue with `TASKQ_MPSAFE`.
- Worker membership is recorded in `struct taskq_thread` so barriers can detect when the caller is already one of the queue's workers.

Lifecycle:
- `taskq_init()` initializes WITNESS state and defers creation of the global queue threads.
- `taskq_create()` allocates and initializes a new queue, then schedules `taskq_create_thread()` so at least one worker exists.
- `taskq_create_thread()` transitions a queue from created to running, creates the configured number of kthreads, and handles the race where a queue is destroyed before its deferred creation runs.
- `taskq_destroy()` marks a queue destroyed, wakes workers, waits for `tq_running` to reach zero, and frees dynamic queues.

Work and barriers:
- `task_set()` initializes a task function, argument, and flags.
- `task_add()` enqueues a task once, sets `TASK_ONQUEUE`, optionally records kcov remote process context, and wakes one worker.
- `task_del()` removes a pending task if still queued.
- `taskq_next_work()` sleeps until work is available or the queue stops, removes the head task, clears `TASK_ONQUEUE`, copies it by value to avoid races with caller-owned task storage, and wakes another worker if more work is queued.
- `taskq_barrier()` and `taskq_del_barrier()` wait until all queue workers have passed through a barrier point; `taskq_do_barrier()` injects barrier tasks and coordinates barrier generations.

Execution model:
- `taskq_thread()` optionally drops the kernel lock for MP-safe queues, registers itself in the queue's thread list, repeatedly runs copied tasks under WITNESS/kcov hooks, calls `sched_pause(yield)` after each task, and exits when the queue is destroyed.
- Barriers are careful about callers already running inside the same taskq, counting that thread directly rather than deadlocking behind its own barrier task.
