# File Research: sources/os/bsd/freebsd-src/sys/sys/timerfd.h

Linux-compatible timerfd user/kernel ABI header.

Key responsibilities:
- Includes `sys/time.h` intentionally to reproduce glibc namespace pollution expected by software using timerfd.
- Defines `timerfd_t` as a 64-bit expiration count type.
- Maps creation flags to `O_NONBLOCK` and `O_CLOEXEC`.
- Defines timer setting flags for absolute time and cancel-on-clock-set behavior.
- Declares userland `timerfd_create`, `timerfd_gettime`, and `timerfd_settime`.
- Declares kernel `timerfd_jumped()` notification hook for clock jumps.

Dependencies:
- Includes `sys/types.h`, `sys/fcntl.h`, and `sys/time.h`.

Notable risks:
- Compatibility depends on matching Linux-visible constants and header side effects closely enough for portable applications.
- Cancel-on-set behavior requires correct kernel notification on realtime clock discontinuities.
