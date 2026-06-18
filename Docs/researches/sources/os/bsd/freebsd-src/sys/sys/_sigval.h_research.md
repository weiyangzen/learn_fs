# File Research: sources/os/bsd/freebsd-src/sys/sys/_sigval.h

Signal value union definitions.

Key elements:
- Under POSIX realtime or XSI visibility, defines `union sigval` with integer and pointer payload variants plus FreeBSD 6 compatibility names.
- For 32-bit compatibility contexts, defines `union sigval32`.

Dependencies:
- Uses visibility macros and `__uint32_t`.

Research notes:
- Used by queued signals, timers, AIO notifications, and other sigevent paths.
- Keeps 64-bit kernels able to represent 32-bit userland pointer payloads.
