# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/adjtime.c

## Purpose
Implements `adjtime` with a syscall-first path and fallback to `/dev/clockctl`.

## Key Elements
Calls `____adjtime50`; if it fails with `EPERM`, opens `_PATH_CLOCKCTL` write-only close-on-exec, caches `__clockctl_fd`, and issues `CLOCKCTL_ADJTIME`.

## Dependencies
Uses `sys/clockctl.h`, `ioctl`, `open`, `errno`, `____adjtime50`, and shared global `__clockctl_fd`.

## Behavior/Risks
Open errors intentionally preserve the original `EPERM`. Once clockctl is opened, later calls always use it, so shared global fd state affects all related time-setting wrappers.
