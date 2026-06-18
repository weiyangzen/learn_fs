# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_event.c

## Role

Implements DragonFlyBSD's kqueue/kevent core: creation of `DTYPE_KQUEUE` file objects, registration/modification/deletion of knotes, event scanning/copyout, wakeups, filter dispatch, per-kqueue and per-knote lifecycle management, and a precise sleep helper for short kevent timeouts. It derives from FreeBSD kqueue code but has DragonFly-specific token, pool-token, LWP, and file descriptor close-race handling.

## Major Entry Points

- `sys_kqueue()` allocates a file descriptor and `struct kqueue`, initializes pending/list queues, installs `kqueueops`, and attaches it to the caller's file descriptor table.
- `sys_kevent()` validates the descriptor as `DTYPE_KQUEUE`, copies in an optional timeout, and calls `kern_kevent()`.
- `kern_kevent()` processes changelist registrations via a caller-supplied copyin function, posts registration errors/receipts, computes timeout deadlines, scans active events, copies out events, and sleeps/reloads markers when no events are pending.
- `kqueue_register()` handles batched registration. It preloads file pointers for fd-backed filters, serializes registration on `kq_regtd`, finds existing knotes by fd klist or kqueue hash, allocates/caches knotes, attaches filters, handles `EV_ADD`, `EV_DELETE`, `EV_ENABLE`, `EV_DISABLE`, `EV_RECEIPT`, `EV_ONESHOT`, `EV_CLEAR`, `EV_DISPATCH`, and fd close races.
- `kqueue_scan()` walks `kq_knpend` with marker knotes, acquires each knote, revalidates fd-backed notes against `fd_closedcounter`, processes active filters, emits `struct kevent`s, clears/requeues/deletes notes according to flags, and respects marker boundaries for concurrent scans.
- `kqueue_close()` terminates all knotes, drops async owner state, and frees the kqueue.

## Filters Implemented Here

- File-backed filters use `filt_fileattach()` to delegate to the underlying file object's `fo_kqfilter()`.
- Kqueue read filter (`EVFILT_READ` on a kqueue) reports pending event count through `filt_kqueue()`.
- Process filter attaches to live or zombie processes via `pfind()`/`zpfind()`, checks jail visibility with `PRISON_CHECK`, tracks `NOTE_EXIT`, `NOTE_FORK`, `NOTE_EXEC`, `NOTE_CHILD`, `NOTE_TRACK`, and detaches on exit.
- Timer filter allocates a callout per knote, enforces global `kern.kq_calloutmax`, sets `EV_CLEAR`, increments `kn_data` on expiration, and handles callout/delete races with `KN_PROCESSING`, `KN_REPROCESS`, and `KN_DELETING`.
- User filter implements `EVFILT_USER`, including `NOTE_TRIGGER`, `NOTE_FFNOP`, `NOTE_FFAND`, `NOTE_FFOR`, `NOTE_FFCOPY`, and compatibility handling for `EV_CLEAR` during modification.
- Filesystem filter (`EVFILT_FS`) uses a global `fs_klist`, sets `EV_CLEAR`, and ORs hints into `kn_fflags`.

## Internal Mechanics

- Knotes use status bits such as `KN_PROCESSING`, `KN_REPROCESS`, `KN_WAITING`, `KN_DELETING`, `KN_DETACHED`, `KN_ACTIVE`, `KN_QUEUED`, and `KN_DISABLED`.
- `knote_acquire()` and `knote_release()` are the core concurrency protocol. They require the related kqueue token and cause contending threads to sleep/retry because a knote may be stale after blocking.
- `KNOTE_ACTIVATE()` marks a knote active and queues it if not already queued or disabled.
- `knote_attach()` indexes a knote either on the referenced file's `f_klist` for fd filters or on the kqueue's hash table for non-fd filters, and also links it into `kq_knlist`.
- `knote_drop()` removes the knote from both indexes, dequeues it if necessary, drops held file references for fd filters, and returns the object to a per-CPU knote cache.
- `knote()`, `knote_insert()`, `knote_remove()`, `knote_assume_knotes()`, and `knote_fdclose()` are exported helper paths used by other subsystems to notify, move, attach, detach, or close fd-associated knotes.

## VFS/File-System Relevance

- Kqueues are file objects and integrate through `struct fileops`; read/write return `ENXIO`, ioctl supports `FIOASYNC` and `FIOSETOWN`, stat reports pending event count as FIFO-like metadata.
- Fd-backed filters depend on underlying file/vnode/socket/device implementations through `fo_kqfilter()`.
- `knote_fdclose()` removes all knotes that reference a closing descriptor and is part of file descriptor/VFS close correctness.
- `EVFILT_FS` exposes filesystem-wide notifications through the global `fs_klist`.
- Process filters interact with exec/fork/exit paths via `KNOTE(&p->p_klist, NOTE_...)`.

## Concurrency and Synchronization

- Uses LWKT pool tokens for kqueues and klists rather than a single global lock.
- Registration is serialized per kqueue with `kq_regtd` and `KQ_REGWAIT` while still supporting recursive registration from `NOTE_TRACK`.
- Scan markers prevent concurrent scans from duplicating or skipping events and support reload/keep/insert modes.
- Close races are addressed by snapshotting `fd_closedcounter`, holding file pointers, and checking `checkfdclosed()` after possible blocking attachment and during scan.
- Non-MPSAFE filters are wrapped with `get_mplock()`/`rel_mplock()`.
- Timer callout paths cannot sleep, so they open-code acquisition behavior and use reprocess flags.

## Tunables and Limits

- `kern.kq_calloutmax` caps timer callouts.
- `kern.kq_checkloop` guards against pathological kevent scan loops.
- `kern.kq_sleep_threshold` determines when precise timeout sleeping should avoid busy looping.
- Per-CPU knote caches retain up to `KNOTE_CACHE_MAX` knotes each.

## Research Notes

- This file is central to polling/select emulation and event notification for the rest of the kernel.
- Any analysis of vnode readiness, file close behavior, process lifecycle notifications, or filesystem event hints should include this file's knote state machine.
- The most fragile areas are the intentional stale-pointer retry loops, fd close interlocks, timer callout deletion races, and marker-based scanning semantics.
