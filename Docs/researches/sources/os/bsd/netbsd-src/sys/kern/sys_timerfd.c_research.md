# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_timerfd.c

Implements Linux-compatible `timerfd` support: timer objects associated with file descriptors, readable when expirations are pending, and integrated with poll/select/kqueue/stat/restart semantics.

Core state:
- `struct timerfd` wraps `struct itimer`, a read condition variable, `selinfo`, waiter count, cancel-on-set/cancelled/restarting flags, and stat timestamps.
- All timerfd state is protected by `itimer_lock()`.

Timer behavior:
- `timerfd_fire`: increments `it_overruns` on each firing and wakes waiters.
- `timerfd_realtime_changed`: handles `CLOCK_REALTIME` changes for `TFD_TIMER_CANCEL_ON_SET`.
- `timerfd_fire_count` and `timerfd_is_readable`: expose pending-expiration/readability state.

Lifecycle:
- `timerfd_create`: allocates and initializes `timerfd`, condition variable, select info, birth time, and underlying `itimer`.
- `timerfd_destroy`: poisons/finalizes the timer, destroys wait structures, and frees memory.

File operations:
- `timerfd_fop_read`: requires an 8-byte read, blocks unless nonblocking, returns `ECANCELED` for cancelled realtime timers, copies expiration count, and resets overruns.
- `timerfd_fop_ioctl`: supports `FIONBIO`, `FIONREAD`, and `TFD_IOC_SET_TICKS`.
- `timerfd_fop_poll`: reports read readiness or records with `selrecord`.
- `timerfd_fop_stat`: reports count/timestamps and FIFO-like mode.
- `timerfd_fop_close`: destroys the timerfd.
- `timerfd_fop_kqfilter`, `timerfd_filt_read`, `timerfd_filt_read_detach`: EVFILT_READ support.
- `timerfd_fop_restart`: wakes blocked reads with restart semantics so close/revalidation can proceed.

Syscalls:
- `do_timerfd_create` / `sys_timerfd_create`: validate clock and flags, allocate fd/file, set `DTYPE_TIMERFD`, apply close-on-exec/nonblock.
- `do_timerfd_gettime` / `sys_timerfd_gettime`: validate fd type and return current timer state.
- `do_timerfd_settime` / `sys_timerfd_settime`: validate flags/times, optionally return old value, convert relative values to absolute deadlines, arm/disarm timer, reset expiration count, and update cancellation/timestamps.

Research notes:
- This file directly exercises generic fd/fileops, select/poll, kqueue, and stat integration patterns relevant to pseudo-files and kernel file descriptor objects.
