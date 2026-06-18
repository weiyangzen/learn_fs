# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/port_subr.c

## Purpose

`port_subr.c` provides shared kernel support for event ports and event sources. It manages event allocation, queue submission/removal, poll wakeups, fd-source cleanup, and kernel event-source association with port file descriptors.

Read completely: 797 lines.

## Main Responsibilities

- Defines the global event-port control structure and `port_max_list` limit.
- Serializes port queue mutations with `port_block()` / `port_unblock()`.
- Implements poll wakeup coordination for ports used as pollable file descriptors.
- Enqueues fired events into a port queue through `port_send_event()`.
- Allocates event structures from the port cache with port resource-limit accounting.
- Frees or invalidates event structures depending on whether they are queued, private, cached, or already delivered.
- Removes fired events from done queues when an association changes or closes.
- Maintains fd-source cache hash buckets and cleans up `portfd_t` objects.
- Associates and dissociates kernel event sources with a port.
- Frees vnode file-operation data attached to event-port-aware vnodes.

## Important Data Structures And Globals

- `port_control`: main framework control object, including the event cache.
- `port_max_list`: maximum list count accepted by bulk port operations.
- `port_queue_t`: per-port queue state, flags, condition variables, source cache, and event lists.
- `port_kevent_t`: allocated event object carrying source, user data, callback, flags, port pointer, and object identity.
- `port_fdcache_t` / `portfd_t`: fd event-source cache records.
- `port_source_t`: per-port kernel source association record with reference count and close callback.

## Control Flow And Algorithms

`port_send_event()` inserts a `port_kevent_t` into the port done queue if it is not already queued, clears wait-for-events state, wakes `port_getn()` waiters when enough events are present, wakes close waiters if all outstanding events are queued, and issues `pollwakeup()` for non-fd sources when needed.

`port_alloc_event()` validates that a user file descriptor refers to a `VPORT`, allocates a `port_kevent_t`, enforces `process.port-max-events` through `port_curr` and `port_max_events`, initializes the event, and releases the file descriptor. `port_alloc_event_local()` does the same with an existing `port_t *`. `port_alloc_event_block()` waits for memory and for an available event slot, returning `EINTR` if interrupted.

`port_free_event()` handles the tricky lifetime cases. Queued non-private events are marked `PORT_KEV_FREE` so `port_get(n)` can skip and free them later. Unqueued, non-cached events decrement `port_curr`, wake waiters, notify close waiters if appropriate, and call `port_free_event_local()`.

`port_remove_done_event()` and `port_remove_fd_object()` temporarily block queue users, push temporary get queues back to the main queue when needed, remove the target done event, invoke dissociation callbacks, and free the backing event structure.

`port_associate_ksource()` creates or references a per-port source association in a hash chain. `port_dissociate_ksource()` decrements its reference count and unlinks/frees it when it reaches zero.

## Dependencies And Integration

- Integrates with vnode/file descriptors through `getf()`, `releasef()`, `VTOEP()`, and `VPORT`.
- Uses poll subsystem support (`pollwakeup`, `polldat_disassociate`) for fd event sources.
- Uses resource controls through `port_max_events` accounting.
- Event source callbacks are invoked for dissociation and source cleanup.

## Locking And Concurrency

`portq_mutex` protects done queues, event counts, wait flags, close coordination, and queue blocking. `port_block()` may sleep and callers must tolerate the queue mutex being dropped/reacquired. `pc_lock` protects fd-cache hash chains. `portq_source_mutex` protects kernel source association lists.

## Notable Risks And Invariants

- `PORT_KEV_DONEQ` prevents duplicate enqueue.
- FD-source events can be submitted from poll wakeup paths; lock release behavior differs for `PORT_SOURCE_FD`.
- Queued events are often invalidated rather than freed immediately to preserve queue traversal and delivery safety.
- `port_curr` must be decremented exactly once for event slots that counted against the port limit.
- Closing a port waits for outstanding event structures to be returned or at least represented in the done queue.

## Research Relevance

Event ports are a scalable notification primitive used by files, pollable objects, timers, and user-level event loops. This file is relevant to filesystem research because file descriptors and vnode-backed objects can register event associations whose lifetime must remain coherent with close, poll, and event retrieval.
