# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_rlimit.c

## Purpose

Implements `/proc/<pid>/rlimit`, a read-only text view of process resource limits.

## Main Entry Point

`procfs_doprocrlimit()`:
- obtains a private reference to the process limit structure with `lim_hold()`.
- iterates all `RLIM_NLIMITS` entries.
- emits `rlimit_ident[i]`, current limit, and maximum limit per line.
- represents `RLIM_INFINITY` as `-1`.
- releases the limit reference with `lim_free()`.

A static assertion ensures `rlimit_ident[]` remains aligned with `RLIM_NLIMITS`.

## Integration Points

Registered by `procfs.c` as `rlimit` with `PFS_RD`.

## Risks and Review Notes

The private limit reference avoids holding the process lock while formatting. Output compatibility depends on `resource.h` maintaining `_RLIMIT_IDENT` names in the expected order.
