# File Research: sources/os/linux/linux/fs/eventpoll.c

## Purpose
Implements Linux `epoll`: anonymous eventpoll files, interest set management, ready-list delivery, nested epoll loop/path checks, file cleanup, busy-poll controls, and epoll syscalls.

## Main Elements
- Core objects: `struct eventpoll` owns the mutex, waitqueues, ready list, overflow list, RB tree of watched descriptors, upward refs, wakeup source, user quota, refcount, and optional busy-poll settings; `struct epitem` represents one watched `(file, fd)` pair and its poll wait entries.
- Ready state machine: `ep_start_scan()` steals `rdllist` and diverts callbacks to `ovflist`; `ep_done_scan()` drains overflow back to the ready list and wakes waiters. Helpers encode scan and per-item overflow state.
- Busy poll support: optional NAPI tracking, timeout/budget/preference ioctls, and IRQ suspend/resume logic are integrated with ready checks.
- Wakeup and poll hooks: `ep_ptable_queue_proc()` registers `ep_poll_callback()` on target waitqueues; callbacks filter masks, queue ready items, handle `EPOLLEXCLUSIVE`, wake `ep->wq` and poll waiters, maintain wakeup sources, update busy-poll NAPI IDs, and implement the `POLLFREE` release/acquire handshake with waitqueue removal.
- Removal and lifetime: `ep_remove()`, `ep_remove_file()`, `ep_remove_epi()`, `eventpoll_release_file()`, and `ep_clear_and_put()` coordinate explicit deletes, epoll-file close, watched-file close, pollwait draining, RB tree erasure, file `f_ep` cleanup, RCU freeing, and `eventpoll` refcounts.
- Polling epoll files: `ep_eventpoll_poll()` and `ep_item_poll()` support polling nested epoll instances with lockdep nesting depth annotations.
- Insertion and modification: `ep_alloc_epitem()`, `ep_register_epitem()`, `ep_insert()`, and `ep_modify()` enforce per-user watch limits, install target-file links, allocate wakeup sources, attach poll callbacks, sample initial readiness, and update event masks with memory barriers.
- Loop and path checks: `ep_ctl_lock()`, `ep_loop_check()`, `ep_loop_check_proc()`, `ep_get_upwards_depth_proc()`, `reverse_path_check()`, and `path_limits[]` prevent cycles, excessive nesting, and excessive wakeup path amplification under `epnested_mutex`.
- Event delivery: `ep_deliver_event()` repolls items, copies events to userspace, handles oneshot and edge-triggered semantics, and requeues level-triggered items; `ep_send_events()` and `ep_poll()` implement wait, timeout, signal, busy-poll, and retry behavior.
- Syscalls and helpers: `epoll_create`, `epoll_create1`, `epoll_ctl`, `epoll_wait`, `epoll_pwait`, `epoll_pwait2`, compat variants, `epoll_sendevents()`, KCMP helper lookup, proc fdinfo, and `eventpoll_init()`.

## Dependencies And Integration
This file is central VFS/poll infrastructure. It integrates with anonymous inodes, waitqueues, file reference and `f_ep` tracking, RCU, RB trees, per-user counters, power-management wakeup sources, sysctl, proc fdinfo, signal-mask helpers, user-copy helpers, optional KCMP, compat syscalls, optional networking busy-poll/NAPI, and epoll UAPI constants.

## Risk Notes
The implementation is dominated by concurrency constraints. Lock ordering across `epnested_mutex`, `ep->mtx`, `file->f_lock`, and `ep->lock` must remain strict. Ready delivery intentionally drops `ep->lock` while copying to userspace, so `ovflist` must catch concurrent callbacks without losing events. File teardown races are handled by file refcount pinning, `f_ep` under `file->f_lock`, RCU freeing, and two-pass pollwait/tree draining. Nested epoll checks must remain atomic with insertion to prevent cycles or wakeup amplification. `POLLFREE`, `EPOLLONESHOT`, `EPOLLET`, `EPOLLEXCLUSIVE`, wakeup sources, and busy-poll all add separate correctness constraints.
