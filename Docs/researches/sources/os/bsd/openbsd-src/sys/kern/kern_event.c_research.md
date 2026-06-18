# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_event.c

## Purpose
Implements OpenBSD kqueue/kevent, knote lifecycle, filter dispatch, poll/select backing kqueues, process/signal/timer/user/file filters, and klist notification infrastructure.

## Main Responsibilities
- Initializes kqueue and knote pools.
- Provides kqueue file operations (`kqueueops`) for descriptor-backed kqueues.
- Creates kqueues through `sys_kqueue()`, `sys_kqueue1()`, and `dokqueue()`.
- Processes changelists and event delivery through `sys_kevent()`.
- Registers, modifies, enables/disables, and deletes knotes via `kqueue_register()`.
- Scans active event queues with marker knotes in `kqueue_scan()`.
- Purges/closes/terminates kqueues safely.
- Supports poll/select through per-thread `p_kq`, serial IDs, and `kqpoll_init()` / `kqpoll_done()` / `kqpoll_exit()`.
- Provides generic `klist` operations for subsystems that own event sources.

## Supported Filters
- `EVFILT_READ` / `WRITE` / `VNODE` / `DEVICE` / `EXCEPT`: file descriptor filters delegated to fileops `fo_kqfilter`.
- `EVFILT_PROC`: process lifecycle events, including `NOTE_EXIT`, `NOTE_FORK`, `NOTE_TRACK`, and `NOTE_EXEC`.
- `EVFILT_SIGNAL`: signal delivery counts.
- `EVFILT_TIMER`: timeout-backed relative/absolute timers with unit validation.
- `EVFILT_USER`: user-triggered events with fflag control operations.
- Special internal filters: `seltrue_filtops`, `dead_filtops`, and `badfd_filtops`.

## Key Data
- `struct kqueue`: active queue, mutex, knote hash/list tables, refcount, state flags, fd table owner.
- `struct knote`: registered event, filterops, status flags, file/process/timer/user state.
- `kqueue_ps_list_lock`: serializes process/signal knote list changes.
- `kq_usereventsmax`: per-process limit for timer/user events.

## Notable Control Flow
`kqueue_register()` validates filter and identifier, finds or allocates a knote, attaches it to the kqueue's fd list or hash, calls filter attach/modify/delete callbacks outside `kq_lock` where needed, handles fd-close races with `fd_checkclosed()`, and activates ready knotes.

`kqueue_scan()` sleeps if no events are active, inserts start/end marker knotes to bound a scan, acquires knotes one at a time, processes filter state, applies oneshot/clear/dispatch rules, handles revoked vnode dead filters, and requeues persistent events.

## Lifetime and Concurrency
Knotes use `KN_PROCESSING` and `KN_WAITING` to serialize concurrent scan/register/remove paths. `knote_acquire()` can drop locks and force callers to restart. Kqueue references are held during scans via `KQREF()` / `KQRELE()`.

## Dependencies
Tied to fd close notifications from `kern_descrip.c`, process fork/exit from `kern_fork.c` and `kern_exit.c`, timeout subsystem, VFS fileops, scheduler task queues, pledge, ktrace, and signal state.

## Research Notes
This is a central event fanout layer. It combines descriptor-indexed knote arrays for fd filters with a hash table for non-fd filters.
