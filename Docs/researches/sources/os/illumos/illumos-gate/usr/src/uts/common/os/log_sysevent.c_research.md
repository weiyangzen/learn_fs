# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/log_sysevent.c

## Purpose

`log_sysevent.c` implements kernel system event publication to `syseventd`. It allocates and packs sysevent buffers, queues events, performs door upcalls to the user daemon, tracks sent-but-not-freed event buffers, supports daemon restart replay, manages sysevent channel registration state, and exposes DDI/user event posting interfaces.

It also maintains a small lofi device-link cache used to communicate devfsadm device-link updates to the lofi driver.

## Event Delivery State

Pending events are held on `log_eventq_head` / `log_eventq_tail`, with count `log_eventq_cnt`. Successfully delivered but not yet freed events are moved to `log_eventq_sent`.

Delivery is controlled by:

- `log_event_delivery`
- `sysevent_upcall_status`
- `sysevent_daemon_init`
- `log_event_cv`
- `async_thread`

The queue has tunable maximum size `logevent_max_q_sz`, default 5000. Threads may block on `event_qfull_cv` if the queue is full and sleeping semantics are allowed.

## Door Upcalls

`log_event_upcall()` performs a kernel door upcall to `syseventd` using `door_ki_upcall_limited()`. It handles:

- `EBADF`: daemon door died; release and clear door handle.
- `EINTR`: short pause and retry.
- `EAGAIN`: exponential backoff, usually while the server process is forking.
- other errors: log and return.

`log_event_pause()` implements the retry delay using `timeout()` and a condition variable.

`log_sysevent_filename()` is called by `syseventd` to set or refresh the door filename. It opens the door, replaces the old handle, and moves all sent-but-uncommitted events back to the pending queue in order so daemon restart can replay them.

`log_sysevent_flushq()` starts the async delivery thread if needed, marks delivery active, runs post-startup setup, and wakes the delivery loop.

## Delivery Thread

`log_event_deliver()` is the async event delivery thread. It runs under CPR callbacks, waits on `log_event_cv`, and delivers pending events in order. For each event, it releases the queue lock during the door upcall. On success, it moves the event from the pending queue to the sent queue. On hold or transport errors, it updates status and sleeps until signaled.

It handles races where a daemon restart moves sent events back to the pending queue while an upcall is in progress by replaying from the new queue head.

## Event Allocation And Attributes

Publisher APIs:

- `sysevent_alloc()`
- `sysevent_free()`
- `sysevent_add_attr()`
- `sysevent_free_attr()`
- `sysevent_attach_attributes()`
- `sysevent_detach_attributes()`
- `sysevent_attr_name()`
- `sysevent_attr_type()`

Events store class, subclass, and publisher strings in aligned payload space. Attributes are represented as nvlists and later repacked into contiguous event buffers by `se_repack()` before queueing.

`sysevent_free()` adjusts payload size when freeing attached nvlist attributes. Packed event buffers are freed by `free_packed_event()`.

## Queueing And IDs

`queue_sysevent()` assigns a monotonically increasing sequence number and high-resolution timestamp, appends the packed event to the pending queue, and wakes the delivery thread if the queue was previously empty.

If the queue is full:

- no transport returns `SE_NO_TRANSPORT`
- no-sleep callers get `SE_EQSIZE`
- sleep callers wait for space

`log_sysevent()` repacks a kernel-created event and queues it. `log_sysevent_new_id()` returns a fresh kernel event ID.

## Sent Event Data APIs

`log_sysevent_copyout_data()` searches `log_eventq_sent` by event timestamp and sequence ID, then copies the event to userland.

`log_sysevent_free_data()` removes a sent event by ID and frees its packed buffer. The source notes that delayed processing may mean the event is not on the sent queue yet and userland may need to retry.

## Channel Registration

The file maintains persistent sysevent channel registration metadata in `registered_channels[]`, protected by `registered_channel_mutex`.

Channel operations include:

- open/close channel
- bind/unbind publisher or subscriber IDs
- register/unregister class/subclass subscriptions
- cleanup IDs
- get registration data

Data structures include channel descriptors, class lists, subclass lists, subscriber bit arrays, and vmem ID allocators. `log_sysevent_register()` copies user arguments, dispatches operations, packs/unpacks nvlist registration data, and copies results back.

## User And DDI Event Posting

`log_usr_sysevent()` accepts a user-provided packed event, copies it into a kernel queue object, notifies lofi for relevant dev events, queues it with no-sleep semantics, and copies the assigned event ID out.

`ddi_log_sysevent()` is the driver-facing API. It builds publisher string `vendor:kern:driver`, allocates a sysevent, attaches attributes if present, posts it with sleep/no-sleep semantics, detaches attributes, frees the event, and maps sysevent errors to DDI return codes.

It rejects `DDI_SLEEP` from interrupt context.

## Lofi Cache

`lofi_nvl_init()` initializes a lock/CV/nvlist cache. `notify_lofi()` watches user-posted `EC_DEV_ADD` and `EC_DEV_REMOVE` events for driver `lofi`, stores/removes instance nvlist data by instance string, and broadcasts cache waiters.

## Concurrency

Important locks:

- `eventq_head_mutex`: pending queue and delivery state.
- `eventq_sent_mutex`: sent queue.
- `event_door_mutex`: door handle.
- `event_qfull_mutex`: queue-full waiters.
- `event_pause_mutex`: retry pause state.
- `registered_channel_mutex`: channel registration database.
- `lofi_devlink_cache.ln_lock`: lofi nvlist cache.

The async delivery thread intentionally releases the pending-queue lock during door upcalls.

## Dependencies

Depends on doors, sysevent structures, nvlists, vmem, DDI/devinfo, modctl event commands, CPR callbacks, timeouts, kernel threads, condition variables, lofi internals, and copyin/copyout.

## Research Notes

Key audit areas are event replay on daemon restart, sent-queue lifetime, queue-full blocking semantics, door error handling, registration table bounds, user buffer copyout sizes, nvlist packing/unpacking, no-sleep allocation paths, and lofi cache trust assumptions for user-posted dev events.
