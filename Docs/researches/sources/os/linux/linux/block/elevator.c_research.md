# File Research: sources/os/linux/linux/block/elevator.c

Implements the block-layer elevator/I/O scheduler core: scheduler registration, queue attachment/detachment, request merge helpers, scheduler sysfs exposure, and runtime scheduler switching.

Key responsibilities:
- Maintains the global registered scheduler list under `elv_list_lock`.
- Provides merge primitives around `q->last_merge`, the elevator hash, scheduler-specific merge callbacks, and request RB-tree helpers.
- Owns `struct elevator_queue` allocation/release, including module references and kobject lifetime.
- Registers scheduler attributes under queue sysfs as `iosched` and coordinates debugfs registration.
- Switches schedulers through queue freeze/quiesce, `q->elevator_lock`, and `tag_set->update_nr_hwq_lock`.

Important functions:
- `elv_merge()`, `elv_attempt_insert_merge()`, `elv_merged_request()`, `elv_merge_requests()` implement the core merge path.
- `elv_rqhash_*()` and `elv_rb_*()` provide reusable scheduler indexing primitives.
- `elv_register()` / `elv_unregister()` manage scheduler types and optional `io_cq` slab caches.
- `elevator_change()`, `elevator_switch()`, `elv_update_nr_hw_queues()` handle scheduler replacement.
- `elv_iosched_show()` / `elv_iosched_store()` back the queue scheduler sysfs attribute.
- `elevator_set_default()` defaults single-queue or shared-tag devices to `mq-deadline` when available.

Concurrency/lifetime notes:
- Scheduler switch paths freeze the queue, cancel blk-mq work, and serialize via `elevator_lock`.
- Sysfs attribute access is blocked once `ELEVATOR_FLAG_DYING` is set.
- Old scheduler resources are released only after unregistering sysfs/debugfs and freeing blk-mq scheduler resources.
- Module lookup/loading is intentionally done before freezing to avoid self-deadlock when the target module resides on the same queue.

Research relevance:
- This is the central policy plug-in layer for Linux block scheduling.
- It links generic request merging with concrete schedulers such as `mq-deadline` and `kyber`.
