# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/error.h

## Role

`error.h` declares common Plan 9-style error-string globals used by the VNC server compatibility and device layers.

## Contents

It declares errors for mount state, lookup, directory/file type mismatches, permissions, bad arguments, I/O, hung-up channels, resource exhaustion, interrupts, malformed stats, and other kernel-like conditions.

## Relationship To Code

- `compat.c`, `dev.c`, `chan.c`, `devcons.c`, `devmouse.c`, `devdraw.c`, and `exportfs.c` raise these strings through `error()`.
- The definitions live in `errstr.h`.

## Notable Limitations And Risk Areas

- These are global character arrays, not enum codes; callers compare and propagate textual errors.
- The set is only what the user-space VNC device environment needs, not a full kernel error catalog.
