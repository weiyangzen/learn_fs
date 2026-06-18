# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/settimeofday.c

## Purpose
Implements `settimeofday` with syscall-first behavior and clockctl fallback.

## Key Elements
Defines shared `int __clockctl_fd = -1`; calls `____settimeofday50`; on `EPERM`, opens `_PATH_CLOCKCTL`, then issues `CLOCKCTL_SETTIMEOFDAY`.

## Dependencies
Uses `sys/clockctl.h`, `ioctl`, `open`, `errno`, and internal `____settimeofday50`.

## Behavior/Risks
This file owns the shared clockctl fd used by other wrappers. Failed fallback deliberately reports `EPERM` rather than the open failure.
