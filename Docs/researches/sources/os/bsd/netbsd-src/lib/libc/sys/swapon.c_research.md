# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/swapon.c

## Purpose
Implements legacy `swapon` via `swapctl`.

## Key Elements
Calls `swapctl(SWAP_ON, __UNCONST(name), 0)`.

## Dependencies
Uses `<sys/swap.h>`, `<unistd.h>`, and `swapctl`.

## Behavior/Risks
Casts away constness for the `swapctl` interface; swap validation and permissions are handled by the syscall.
