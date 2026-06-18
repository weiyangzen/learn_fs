# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/ppoll.c

## Purpose
Implements `ppoll` over NetBSD's `pollts`.

## Key Elements
Passes fds, nfds, timeout `timespec`, and signal mask directly to `pollts`.

## Dependencies
Uses `<sys/poll.h>`, `<sys/time.h>`, and libc namespace handling.

## Behavior/Risks
Thin adapter; all timeout, signal-mask, and polling semantics are delegated to `pollts`.
