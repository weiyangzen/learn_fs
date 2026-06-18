# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/eventfd_write.c

## Purpose
Implements the `eventfd_write` helper.

## Key Elements
Writes exactly one `eventfd_t` value to the descriptor.

## Dependencies
Uses `<sys/eventfd.h>`, `write`, and `errno`.

## Behavior/Risks
Short writes are converted to `EIO`; otherwise behavior is delegated to the descriptor's eventfd implementation.
