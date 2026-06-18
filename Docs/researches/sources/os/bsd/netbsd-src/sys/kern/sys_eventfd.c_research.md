# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_eventfd.c

## Purpose
Implements NetBSD's Linux-compatible `eventfd(2)` object: a file descriptor wrapping a 64-bit counter that can be read, written, polled, selected, and monitored with kqueue.

## Main Interfaces
- `do_eventfd`, `sys_eventfd`: validate `EFD_CLOEXEC`, `EFD_NONBLOCK`, and `EFD_SEMAPHORE`; allocate a descriptor; attach `DTYPE_EVENTFD` fileops.
- `eventfd_fop_read`: blocks until counter is nonzero, then returns either `1` in semaphore mode or the whole counter and resets it.
- `eventfd_fop_write`: imports an `eventfd_t`, rejects overflow sentinel, blocks until the value fits, then increments the counter.
- `eventfd_fop_poll`, `eventfd_fop_kqfilter`: expose read/write readiness and EVFILT_READ/EVFILT_WRITE notifications.
- `eventfd_ioctl`, `eventfd_fop_stat`, `eventfd_fop_close`, `eventfd_fop_restart`.

## State And Control Flow
`struct eventfd` owns a mutex, read/write condition variables, read/write `selinfo`, counter value, waiter count, restart flag, semaphore flag, and timestamps. Blocking read/write paths loop under `efd_lock`, call `eventfd_wait`, update timestamps, and use `eventfd_wake` to notify the opposite side. `fo_restart` sets `efd_restarting` and broadcasts to convert blocked syscalls to `ERESTART` so descriptor close/revalidation can proceed.

## Dependencies And Integration
Uses NetBSD file descriptor allocation (`fd_allocfile`, `fd_affix`), generic `fileops`, `uiomove`, `selnotify`, kqueue filterops, stat metadata, process credentials, and descriptor close-on-exec handling.

## Risks And Edge Cases
- `eventfd_destroy` asserts no waiters; correctness depends on `fo_restart` and descriptor lifecycle waking blocked readers/writers before final close.
- Write-side error handling manually restores `uio_resid` after an earlier `uiomove` so generic write accounting reports the error correctly.
- `FIONSPACE` passes through because available write space depends on the specific value being written.
- The implementation never reports Linux's kernel-internal overflow `POLLERR` case because normal userspace read/write cannot create it.

## Filesystem Relevance
Indirect but important file-descriptor substrate. It implements a pseudo-file object with `fileops`, stat, poll, and kqueue behavior but no VFS vnode or persistent filesystem state.
