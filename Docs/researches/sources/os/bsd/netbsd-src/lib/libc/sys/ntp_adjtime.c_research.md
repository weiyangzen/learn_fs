# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/ntp_adjtime.c

## Purpose
Implements `ntp_adjtime` with syscall-first behavior and clockctl fallback.

## Key Elements
Calls `__ntp_adjtime(tp)` unless `__clockctl_fd` is already open. On `EPERM`, opens `_PATH_CLOCKCTL`, issues `CLOCKCTL_NTP_ADJTIME`, and returns `args.retval` because ioctl cannot directly return the syscall return value.

## Dependencies
Uses `sys/timex.h`, `sys/clockctl.h`, `ioctl`, `open`, `errno`, and shared `__clockctl_fd`.

## Behavior/Risks
Special handling preserves unprivileged `tp->modes == 0` syscall behavior before falling back. Return-value mapping through `args.retval` is a key ABI detail.
