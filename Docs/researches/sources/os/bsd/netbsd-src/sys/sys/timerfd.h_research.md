# File Research: sources/os/bsd/netbsd-src/sys/sys/timerfd.h

Read completely: 67 lines.

Defines NetBSD’s Linux-compatible timerfd interface.

Key elements:
- Defines timerfd flags mapped to existing file flags: `TFD_TIMER_ABSTIME`, `TFD_TIMER_CANCEL_ON_SET`, `TFD_CLOEXEC`, and `TFD_NONBLOCK`.
- Defines `TFD_IOC_SET_TICKS` ioctl for setting expiration tick count.
- Kernel declarations expose `do_timerfd_create`, `do_timerfd_gettime`, and `do_timerfd_settime`.
- Userland declarations expose `timerfd_create`, `timerfd_gettime`, and `timerfd_settime`.

Risks and notes:
- Linux compatibility depends on matching expected flag behavior.
- `TFD_TIMER_ABSTIME` and `TFD_TIMER_CANCEL_ON_SET` reuse open flag values intentionally.
