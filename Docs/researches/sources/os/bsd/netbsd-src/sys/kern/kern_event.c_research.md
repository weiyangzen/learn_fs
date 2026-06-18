# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_event.c

Read completely: 3042 lines.

Implements NetBSD's kqueue/kevent subsystem, including kqueue file operations, kevent registration/scanning, built-in and dynamically registered filters, knote lifetime management, process/timer/user filters, klist helpers used by backing objects, and the kernel-facing notification API.

Core structures and filter registry:
- `struct knote_impl` wraps public `struct knote` with a private in-flux counter and per-knote filter-operation lock.
- `sys_kfilters[]` maps built-in filters: read, write, vnode, proc, signal, timer, fs, user, empty, and placeholders for unsupported AIO.
- `kfilter_register()` and `kfilter_unregister()` maintain dynamically registered user filters under `kqueue_filter_lock`, with per-filter refcounts preventing unregister while in use.
- `kqueue_init()` initializes the filter lock and registers a kauth listener that permits process-event monitoring for same-uid non-SUGID processes.

Locking and lifetime model:
- The file documents a strict order: `kqueue_filter_lock` -> filedesc `fd_lock` -> knote `foplock` -> backing-object lock -> kqueue spin lock.
- `filter_attach()`, `filter_detach()`, `filter_event()`, and `filter_touch()` wrap filterops and acquire the big kernel lock for non-MPSAFE filters.
- `klist_fini()` neuters knotes by replacing their filterops with no-op stubs while holding each knote's foplock, preventing use-after-free of backing objects or module code.
- The in-flux protocol (`kn_enter_flux()`, `kn_leave_flux()`, `kn_wait_flux()`, `knote_detach_quiesce()`) lets complex submitters such as process fork tracking drop locks temporarily while preventing concurrent detach/free.

Kqueue system calls and file operations:
- `kqueue1()`, `sys_kqueue()`, and `sys_kqueue1()` allocate a kqueue file, initialize `kq_lock`, CV, select state, queue head, descriptor state, and optional close-on-exec.
- `sys___kevent100()` and `kevent1()` copy in changes in bounded chunks, register each change, optionally return EV_RECEIPT/EV_ERROR results, then scan for pending events.
- `kqueue_ioctl()` maps filter IDs to names and names to filter IDs for `KFILTER_BYFILTER` and `KFILTER_BYNAME`.
- `kqueue_poll()`, `kqueue_stat()`, `kqueue_kqfilter()`, `kqueue_restart()`, and `kqueue_close()` provide normal file behavior for kqueue descriptors.
- `kqueue_close()` marks `KQ_CLOSING`, walks fd-attached and hash-attached knote lists, detaches all knotes, then destroys kqueue resources.

Registration and scanning:
- `kqueue_register()` validates filters, finds existing knotes by fd list or internal hash, handles `EV_ADD`, `EV_DELETE`, enable/disable updates, `f_touch` updates for supported filters, immediate `f_event` checks, and filter refcounts.
- `kqueue_scan()` waits with optional timeout, uses a marker knote to bound queue traversal, coordinates with in-flux/detaching knotes, re-polls non-oneshot events, copies out events in chunks, handles `EV_ONESHOT`, `EV_CLEAR`, and `EV_DISPATCH`, and wakes flux waiters when traversal state changes.
- `knote_enqueue()`, `knote_activate_locked()`, `knote_activate()`, and `knote_deactivate_locked()` maintain the active/queued state, event count, CV wakeups, and select notifications.
- `knote_detach()` removes a knote from the monitored object, descriptor/hash table, and kqueue queue, drops fd references for fd filters, decrements filter refcount, and frees the knote.

Built-in filters:
- File filters (`EVFILT_READ`, `EVFILT_WRITE`, `EVFILT_VNODE`, `EVFILT_EMPTY`) delegate attach to the file's `fo_kqfilter`.
- Kqueue-read filters report pending kqueue event count and are used when monitoring a kqueue descriptor.
- Process filters attach to `p_klist`, enforce kauth, mask user-provided internal `NOTE_CHILD`, and support `NOTE_EXEC`, `NOTE_FORK`, `NOTE_TRACK`, `NOTE_TRACKERR`, and `NOTE_EXIT`.
- `knote_proc_exec()`, `knote_proc_fork()`, and `knote_proc_exit()` submit process lifecycle notifications; fork tracking allocates both a one-shot `NOTE_CHILD` event and a new child-tracking knote.
- Timer filters convert event data across seconds/milliseconds/microseconds/nanoseconds, support relative and absolute `NOTE_ABSTIME`, allocate callouts with a global limit, reschedule repeating timers, and support safe reconfiguration through `f_touch`.
- User filters are purely kqueue-local and support `NOTE_TRIGGER`, `NOTE_FFNOP`, `NOTE_FFAND`, `NOTE_FFOR`, `NOTE_FFCOPY`, `EV_CLEAR`, and `f_touch`.
- `seltrue_filtops` and `seltrue_kqfilter()` provide always-ready read/write filters for simple devices.

Klist API:
- `knote()` walks a backing object's `klist` and activates knotes whose `f_event` returns true; the backing object is assumed to hold its own lock.
- `knote_fdclose()` detaches all knotes for a closing file descriptor.
- `knote_set_eof()` and `knote_clear_eof()` update EOF flags under the kqueue lock.
- `klist_init()`, `klist_fini()`, `klist_insert()`, and `klist_remove()` are the backing-object list helpers.

Risks and notes:
- The in-flux detach protocol is essential; violating it can free knotes while fork tracking or scan traversal still expects them to exist.
- `filter_touch()` is deliberately allowed only for known-safe timer and user filters during registration because it does not take the foplock.
- `kqueue_register()` contains a comment noting `hashinit()` can block while `fd_lock` is held.
- Process fork tracking uses `KM_NOSLEEP`; allocation failure is reported as `NOTE_TRACKERR`.
- Timer callouts are globally capped by `kq_calloutmax`; attaching a timer can fail with `ENOMEM`.
- Kqueue stat reports a dummy FIFO-like object with size equal to pending events.
