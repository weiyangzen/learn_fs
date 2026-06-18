# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/timerfd.h

## Purpose
Timer file descriptor ABI header providing Linux-compatible timerfd constants and illumos ioctl commands.

## Main Interfaces
- Defines `TFD_CLOEXEC`, `TFD_NONBLOCK`, `TFD_TIMER_ABSTIME`, and `TFD_TIMER_CANCEL_ON_SET`.
- Defines timerfd ioctl base `TIMERFDIOC` and commands `TIMERFDIOC_CREATE`, `TIMERFDIOC_SETTIME`, and `TIMERFDIOC_GETTIME`.
- Defines `timerfd_settime_t` with file descriptor, flags, and `itimerspec`.
- User declarations include `timerfd_create`, `timerfd_settime`, and `timerfd_gettime`.
- Kernel minor names include `TIMERFDMNRN_TIMERFD` and `TIMERFDMNRN_CLONE`.
- Defines `TIMERFD_VALMAX` and Linux monotonic clock value `TIMERFD_MONOTONIC`.

## Dependencies And Relationships
Includes `sys/types.h` and `sys/time_impl.h`. It links the public libc timerfd calls to the kernel timerfd pseudo-device/ioctl implementation.

## Research Notes
The constants intentionally mirror Linux flag values where needed for compatibility, while the actual kernel interface is ioctl-based.
