# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/plan9.c

Plan 9 host adapter for ISO image building.

Key behavior:
- `dirtoxdir` converts Plan 9 `Dir` metadata to `XDir`, atomizing name/uid/gid, copying mode, atime, mtime, length, and using numeric uid/gid zero.
- `fdtruncate` is a no-op stub on Plan 9.

Research notes:
- Contrasts with `unix.c`, which uses POSIX `ftruncate` and passwd/group lookups.
