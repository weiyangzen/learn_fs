# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/truncate.c

## Purpose
Implements `truncate` as a padded syscall wrapper.

## Key Elements
Calls `__truncate(path, 0, length)`.

## Dependencies
Uses syscall headers, `<unistd.h>`, and internal `__truncate`.

## Behavior/Risks
Maintains historical 64-bit offset padding for the path-based truncate syscall.
