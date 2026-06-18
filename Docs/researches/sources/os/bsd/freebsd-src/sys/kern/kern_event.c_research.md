# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_event.c

Read status: complete file reviewed.

This file implements FreeBSD's kqueue/kevent core and the generic knote/knlist machinery used by many kernel objects to publish readiness and lifecycle events. It defines kqueue file operations, kevent syscall handling, filter registration, event scanning, notification delivery, timer/user/process/jail filters, kqueue fork-copy support, and sysctl export of process kqueue state.

Main entry points include `sys_kqueue`, `sys_kqueuex`, `kern_kqueue`, `sys_kevent`, `kern_kevent`, `kern_kevent_fp`, `kern_kevent_anonymous`, `kqfd_register`, `kqueue_add_filteropts`, `kqueue_del_filteropts`, `knote`, `knlist_add`, `knlist_remove`, `knlist_cleardel`, `knote_fdclose`, `knote_fork`, `knote_triv_copy`, and `kern_proc_kqueues_out`. The `kqueueops` table exposes kqueues as file descriptors with ioctl, poll, kqfilter, stat, close, fork, and kinfo handlers.

Core state is built around `struct kqueue`, `struct knote`, per-kqueue fd lists and non-fd hash lists, the global `sysfilt_ops[]` filter table, `knote_zone`, and `kq_ncallouts` bounded by `kern.kq_calloutmax`. Locking is central: `kq_lock` serializes each queue, `kq_global` orders nested kqueue interactions, `filterops_lock` protects dynamic filter refs, and `kn_influx` plus `KQ_FLUXWAIT` coordinates teardown or modification while a knote is being scanned or copied.

The syscall path copies change records in bounded `KQ_NEVENTS` batches, registers or updates knotes with `kqueue_register`, then drains ready events through `kqueue_scan`. `kqueue_scan` handles blocking timeouts, disabled knotes, oneshot/drop semantics, event revalidation, EV_CLEAR/EV_DISPATCH behavior, batched copyout, and wakeups for threads waiting on in-flux knotes. Capability rights are enforced via `CAP_KQUEUE_CHANGE` and `CAP_KQUEUE_EVENT`.

Built-in filters include fd-backed file/vnode/socket-style filters delegated to `fo_kqfilter`, kqueue-read filters, process filters with `NOTE_EXIT`, `NOTE_EXEC`, `NOTE_FORK`, and `NOTE_TRACK`, jail filters, callout-backed timers with absolute/relative sbintime support, and EVFILT_USER state machines. Timer filters maintain per-knote callout data, pause timers for stopped/killed processes, enforce the global callout cap, and support re-add touch updates.

Lifecycle paths are extensive. `kqueue_drain` marks a queue closing, waits for extra refs, drops all knotes, drains taskqueue work, and wakes poll/select waiters. `kqueue_close` removes the queue from the filedesc list and releases credentials and accounting. `knote_drop` and `knote_drop_detached` detach from source knlists, remove queue membership, release fd and filter refs, and free UMA knotes. `knlist_detach` supports autodestroy lists, while `knlist_cleardel` handles disappearing event sources.

Fork support implements `KQUEUE_CPONFORK`: `kqueue_fork_alloc` creates the destination kqueue, and `kqueue_fork_copy_*` copies eligible knotes with filter-specific `f_copy` hooks while respecting fd validity, fhold, knlist membership, active queue state, and in-flux markers.

Integration points include file descriptor tables, proc/jail lifecycle notification, callouts, taskqueues, Capsicum rights, poll/select, sysctl `kern.proc.kq`, KTRACE compatibility, 32-bit compat conversion, and external filterops from signal and filesystem modules.

Risk areas are lock ordering and in-flux correctness, fd reuse races around `fget_noref_unlocked`, nested kqueue notification recursion, timer callout drain/reschedule races, process tracking note creation under `NOTE_TRACK`, and exact queue count accounting under EV_CLEAR, EV_DISPATCH, EV_ONESHOT, and EV_DROP paths.
