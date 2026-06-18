# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/portfs/port.c

## Role

Core event-port syscall implementation for illumos `portfs`. It registers the `portfs` system call module, creates event-port vnodes/file descriptors, dispatches all user-facing port operations, manages per-port queues, alert mode, waiting threads, event copyout, timeout handling, source registration, and kstats.

## Major Responsibilities

- Defines the `portfs` syscall entry and 32-bit wrapper.
- Implements `PORT_CREATE`, `PORT_GET`, `PORT_GETN`, `PORT_ASSOCIATE`, `PORT_DISSOCIATE`, `PORT_SEND`, `PORT_SENDN`, `PORT_DISPATCH`, and `PORT_ALERT`.
- Creates `VPORT` vnodes backed by `port_t`.
- Enforces resource controls:
  - `project.port-max-ids` for number of ports.
  - `process.port-max-events` for per-port event capacity.
- Initializes per-port queues, source cache, fd cache skeleton, ownership metadata, and timestamps.
- Pre-associates static kernel event sources such as AIO.
- Sends user and library events into the queue.
- Implements alert mode, which wakes all waiters and returns `PORT_SOURCE_ALERT`.
- Implements `port_getn()` queue draining, temporary get-list use, callback-based delivery filtering, native/ILP32 copyout, timeout looping, and poll wakeups.

## Key Functions

- `_init()` builds dummy VFS/vnode ops, initializes global `port_control`, creates `port_cache`, installs kstats, and installs the syscall module.
- `portfs()` is the main syscall dispatcher. It validates port file descriptors and routes to creation, get, associate, send, dispatch, dissociate, and alert operations.
- `port_create()` allocates `port_t`, creates a `VPORT` vnode, allocates a file descriptor, applies rctl checks, increments global counts, and calls `port_init()`.
- `port_init()` initializes locks, event queues, source cache, fd cache skeleton, metadata, and static kernel sources.
- `port_send()` allocates and posts a `PORT_SOURCE_USER` event.
- `port_dispatch_event()` posts private library/kernel events, optionally marking them non-shareable.
- `port_sendn()` sends one user event to multiple port descriptors and returns per-entry errors through the caller’s error array.
- `port_alert()` stores alert state and signals every currently waiting getter.
- `port_getn()` is the central retrieval engine. It handles counting mode, alert mode, blocking and nonblocking waits, timeout conversion, temporary queue transfer, callback validation, free/discard semantics, copyout, and wakeup handoff.
- `port_copy_event()` and `port_copy_event32()` convert kernel events to user ABI records and invoke source callbacks before final delivery.
- `port_get_timeout()` converts native or 32-bit timeout structures.
- `port_queue_thread()` orders waiters by requested event count, favoring smaller requests.
- `port_get_kevent()` iterates event lists for both normal get and close paths.
- `port_kstat_init()` exposes the number of active event ports.

## Event Queue Semantics

Events are queued as `port_kevent_t` records. `port_getn()` moves the main queue into `portq_get_list` before callback processing so new producers can continue enqueueing without being blocked by potentially slow delivery callbacks.

Delivery is callback-mediated. A source callback can update event bits, release source resources, or deny delivery to the current process. Denied events are reinserted into the temporary list, which is important for shared ports where non-shareable or owner-specific events must remain available to the right process.

`PORT_KEV_FREE` events are discarded during retrieval. Wired/cached events remain under their source’s ownership; default events return to the port cache after delivery.

## Alert Mode

Alert mode is modeled as port state, not a normal queued event. `port_alert()` sets `PORTQ_ALERT`, records event/user payload and owner pid, and marks all current waiters with per-thread alert data. Future `port_get()`/`port_getn()` calls return the alert event immediately until alert mode is cleared.

## Concurrency And Locking

- `port_control.pc_mutex` protects global port counts.
- `port_mutex` protects per-port close/init state.
- `portq_mutex` protects queue state, waiters, alert state, close state, and poll flags.
- `portq_source_mutex` protects the per-port source cache.
- `port_block()`/`port_unblock()` serialize queue-drain operations against other getters.
- `port_getn()` deliberately drops `portq_mutex` while invoking callbacks and preparing user records, after moving events to a temporary queue.
- Close coordination uses `portq_thrcnt`, `portq_getn`, `PORTQ_CLOSE`, and `portq_closecv`.

## Dependencies

This file depends on vnode operations from `port_vnops.c`, fd association logic from `port_fd.c`, file-watch association logic from `port_fop.c`, kernel event source APIs declared through `sys/port_impl.h`, AIO close callbacks, rctl, kstats, and poll wakeup integration.

## Research Notes

This file is the control-plane center of event ports. The most important behavior is the separation between event allocation/posting and event delivery. Event sources reserve slots up front, queue completed events later, and reclaim or reuse slots through callback and flag semantics during `port_getn()`.
