# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/clock_settime.c

## Purpose
Implements `clock_settime` with fallback through clockctl.

## Key Elements
Tries `____clock_settime50`; on `EPERM`, opens `_PATH_CLOCKCTL`, caches `__clockctl_fd`, fills `clockctl_clock_settime`, and uses `CLOCKCTL_CLOCK_SETTIME`.

## Dependencies
Uses `sys/clockctl.h`, `ioctl`, `open`, `errno`, `____clock_settime50`, and the shared `__clockctl_fd`.

## Behavior/Risks
Preserves `EPERM` if clockctl cannot be opened. Global fd caching means the fallback decision is process-wide across the clockctl wrappers.
