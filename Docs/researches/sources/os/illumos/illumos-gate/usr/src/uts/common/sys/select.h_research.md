# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/select.h

## Role

Defines `fd_set`, descriptor-set manipulation macros, `select()`, and `pselect()` declarations with illumos standards-visibility handling.

## Key Interfaces

- Duplicates `sigset_t` where necessary to avoid inclusion-order problems with `signal.h`.
- Default `FD_SETSIZE` is `65536`.
- Defines `fd_mask`, `fds_mask`, `NFDBITS`, `FD_NFDBITS`, `howmany`, and `__howmany`.
- `fd_set` stores descriptor bits in `long fds_bits[]`.
- `FD_SET`, `FD_CLR`, `FD_ISSET`, and `FD_ZERO` manipulate descriptor sets.
- Userland declares `select()` and, under the appropriate namespace, `pselect()`.

## Compatibility Notes

The header carefully gates type names and prototypes for X/Open, POSIX, extensions, kernel, and fake-kernel builds. `FD_ZERO` maps to `bzero()` in kernel-like builds and `_memset()` in userland.

## Risk Notes

`fd_set` size and bit arithmetic are ABI-visible. Changes to `FD_SETSIZE`, word sizing, or standards gates affect application binary and source compatibility.
