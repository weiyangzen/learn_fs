# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/accept4.c

## Purpose
Implements `accept4` in terms of NetBSD's `paccept`.

## Key Elements
Passes socket, address, address length, `NULL` signal mask, and flags to `paccept`.

## Dependencies
Uses `<sys/socket.h>` and libc namespace handling.

## Behavior/Risks
Thin semantic adapter; behavior is delegated to `paccept`, so flag validation and accept behavior live there.
