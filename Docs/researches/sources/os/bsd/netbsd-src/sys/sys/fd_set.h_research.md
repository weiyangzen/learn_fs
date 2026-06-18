# File Research: sources/os/bsd/netbsd-src/sys/sys/fd_set.h

Read completely: 108 lines.

## Purpose
Defines `fd_set` and macros for select-style file descriptor bitsets.

## Main Interfaces
- Internal type: `__fd_mask`.
- Bit geometry: `__NFDBITS`, `__NFDSHIFT`, `__NFDMASK`.
- Default `FD_SETSIZE` of 256.
- `fd_set` with `fds_bits`.
- Macros: `FD_SET`, `FD_CLR`, `FD_ISSET`, `FD_ZERO`, and NetBSD-visible `FD_COPY`, `fd_mask`, `NFDBITS`.

## Dependencies And Integration
Used by `select(2)` and descriptor readiness code. Includes feature-test and machine integer types.

## Risks And Edge Cases
- `FD_SETSIZE` may be user-defined before inclusion.
- Macros do not bounds-check descriptor indices.
- `FD_ZERO`/`FD_COPY` use compiler builtins when available.

## Filesystem Relevance
Moderate. Filesystem descriptors participate in readiness APIs, especially for special files and devices.
