# File Research: sources/os/bsd/freebsd-src/sys/kern/sys_timerfd.c

## Purpose
Implements Linux-style timer file descriptors for FreeBSD, including descriptor creation, read semantics, timer programming, realtime-clock jump handling, poll/kqueue readiness, stat/kinfo, and close cleanup.

## Main Elements
- `struct timerfd`: stores user timer spec, clock id, creation flags, timer flags, expiration count, callout, select/kqueue state, cached boottime, realtime-jump state, timestamps, and synthetic inode.
- Global `timerfd_list`: tracks active timerfds so `timerfd_jumped()` can update realtime absolute timers after discontinuous clock changes.
- `timerfd_jumped()`: detects `CLOCK_REALTIME` absolute timer effects, marks cancel-on-set timers `ECANCELED`, handles backward jumps, adjusts pending absolute callouts, and wakes waiters.
- `timerfd_read()`: returns an 8-byte expiration count, blocks or returns `EAGAIN` if no expirations, and implements jump/cancel read semantics.
- `timerfd_ioctl()`: supports `FIOASYNC` and `FIONBIO` by updating file flags.
- `timerfd_poll()`, `timerfd_kqfilter()`, `filt_timerfdread()`: expose readable readiness when expiration count is nonzero and no consumed jump state blocks reporting.
- `timerfd_stat()`, `timerfd_fill_kinfo()`, `timerfd_close()`: report descriptor metadata, export kinfo details, remove from global list, drain callout/select state, and free memory.
- `timerfd_expire()`: callout handler that increments expiration count, accounts for missed periodic expirations, reschedules intervals, clears one-shot timers, and wakes readers.
- `kern_timerfd_create()`, `kern_timerfd_gettime()`, `kern_timerfd_settime()`: kernel implementations for syscall wrappers, validating clocks/flags/timespecs and manipulating descriptor state.
- `sys_timerfd_create()`, `sys_timerfd_gettime()`, `sys_timerfd_settime()`: user copyin/copyout syscall entry points.

## Dependencies And Integration
Uses `struct fileops`, file descriptor allocation, callouts, selinfo/kqueue, unr inode allocation, audit, timespec helpers, boottime/nanouptime conversion, Capsicum rights through `fget()`, and generated syscall entries for timerfd syscall numbers.

## Risk Notes
Clock conversion is subtle: absolute realtime timers are converted relative to cached boottime, and realtime jumps can cancel or adjust timers. Periodic expiration counting must avoid losing missed intervals. The file uses `cap_write_rights` for get/set fd lookup, which is worth verifying against intended Capsicum rights policy for read-only gettime use.
