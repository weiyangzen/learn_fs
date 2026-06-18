# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/execx.h

## Role

`execx.h` defines the public extension for `execvex()`, an exec variant that can take flags.

## Definitions

- Defines `EXEC_DESCRIPTOR`, meaning the first `execvex()` argument is interpreted as an already-open file descriptor in the calling process rather than a pathname.
- Outside the kernel, declares `execvex(uintptr_t, char *const *, char *const *, int)`.
