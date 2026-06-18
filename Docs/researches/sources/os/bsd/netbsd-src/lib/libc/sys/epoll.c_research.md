# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/epoll.c

## Purpose
Provides Linux-compatible epoll convenience wrappers over NetBSD's `epoll_pwait2`.

## Key Elements
`epoll_create` validates positive size and calls `epoll_create1(0)`. `epoll_wait` delegates to `epoll_pwait` with no signal mask. `epoll_pwait` converts millisecond timeout to `timespec` or `NULL` for infinite wait.

## Dependencies
Uses `<sys/epoll.h>`, signal/time types, `errno`, and `epoll_pwait2`.

## Behavior/Risks
Negative timeout becomes infinite. Timeout conversion is millisecond-based and uses stack `timespec` passed directly to `epoll_pwait2`.
