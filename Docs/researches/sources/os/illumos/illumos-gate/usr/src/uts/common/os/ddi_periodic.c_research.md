# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_periodic.c

## Role

`ddi_periodic.c` implements `ddi_periodic_add(9F)` and `ddi_periodic_delete(9F)` through the cyclic subsystem. It provides DDI-visible periodic callbacks at IPL 0 through IPL 10, either in kernel taskq context or via soft interrupt queues.

The implementation deliberately prevents overlapping executions of the same periodic handler and tightens cancellation semantics so the deleting caller blocks until the handler is no longer dispatched or executing.

## Core Objects and Globals

Each periodic registration has a `ddi_periodic_impl_t` allocated from `periodic_cache`, an opaque ID from `periodic_id_space`, a cyclic ID, lock/CV, preallocated taskq entry, handler, argument, level, interval, flags, and execution thread pointer.

Global state includes:
- `periodics`, the list of all active periodics;
- `periodic_softint_queue[10]` for IPL 1 through IPL 10;
- `periodic_taskq` for IPL 0 work;
- `periodics_lock`, protecting the global list and soft interrupt queues.

Tunables set max ID, taskq thread count, and base resolution. The minimum supported interval is 10 ms by default.

## Registration and Dispatch

`ddi_periodic_init()` creates the cache, active list, ID space, soft interrupt queues, taskq, and global mutex. `ddi_periodic_fini()` deletes any remaining periodics, destroys the taskq, ID space, cache, lists, and mutex.

`i_timeout()` is the implementation behind periodic add. It allocates a periodic, stores handler metadata, rounds intervals up to the supported resolution, creates a cyclic at `CY_LOCK_LEVEL`, and only then inserts the periodic into the visible global list before returning the opaque ID.

`periodic_cyclic_handler()` runs when the cyclic fires. It skips cancelled or already-dispatched periodics, marks the object dispatched, and either dispatches `periodic_execute()` to the taskq for IPL 0 or queues the object on the appropriate soft interrupt list and calls `sir_on(level)`.

`ddi_periodic_softintr()` drains the queue for one soft interrupt level and executes each pending periodic.

## Execution and Cancellation

`periodic_execute()` verifies the object is dispatched but not executing, checks cancellation, marks `DPF_EXECUTING`, records `curthread`, drops the lock, calls the consumer handler, then clears execution and dispatch flags, increments fire count, and broadcasts the CV.

`i_untimeout()` removes the periodic from the global list so only one deletion caller owns final cleanup. It panics if called from the periodic's own handler to avoid self-deadlock, marks the object cancelled, removes the cyclic under `cpu_lock`, waits for dispatched/executing flags to clear, and frees the ID, CV, lock, and cache object.

## Locking and Error Behavior

The file documents lock ordering: do not hold an individual periodic lock while acquiring `periodics_lock`. Objects in soft interrupt queues are protected from free by the dispatched flag. Cancellation waits for both dispatch queue removal and handler completion.

The implementation uses `VERIFY()` heavily for invariant checks. It warns and rounds up when a caller asks for a finer period than supported.

## Subset Relevance

Periodic callbacks are general OS driver infrastructure. Storage and filesystem-adjacent drivers may use this DDI service for polling, maintenance, or timeout-like periodic work.
