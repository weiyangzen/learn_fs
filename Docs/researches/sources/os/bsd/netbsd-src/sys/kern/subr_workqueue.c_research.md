# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_workqueue.c

Read completely: 484 lines.

This file implements kernel workqueues: deferred callbacks executed by kernel worker threads, either one queue per workqueue or one queue per CPU.

Structures:
- `workqueue` stores callback, callback argument, flags, name, priority, and original allocation pointer.
- `workqueue_queue` stores the pending simple queue, mutex, condvar, generation counter, and worker LWP.
- `struct work` is treated as a `work_impl_t` queue node.

Main behavior:
- `workqueue_create` allocates cacheline-aligned storage and creates one worker or per-CPU workers.
- `workqueue_worker` sleeps until pending work exists, moves pending work to a local batch, marks `q_gen` odd while running, executes callbacks outside the queue lock, increments generation when done, and wakes waiters.
- `workqueue_enqueue` appends a work item and signals the worker.
- `workqueue_wait` waits until a given work item is no longer pending or in the current running batch, using `q_gen` to detect active batches.
- `workqueue_destroy` swaps the callback to `workqueue_exit`, queues exit work to each worker, waits for thread exit, and frees storage.

Integration: `subr_vmem.c` uses workqueues for periodic rehashing. The API is a general kernel deferral mechanism and includes SDT probes for create, enqueue, entry/return, wait, and destroy.

Reliability notes: callers must ensure no new work is enqueued before `workqueue_wait` if they need precise completion semantics. Waiting from the worker itself is detected and returns without blocking to avoid deadlock. Debug builds catch duplicate pending enqueue of the same work item.
