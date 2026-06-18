# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs.h

## Purpose

Declares the kernel-only procfs filler, attribute, and visibility callback prototypes shared by `procfs.c` and per-file procfs implementations.

## Interface

Declared filler callbacks:
- `procfs_docurproc()`
- `procfs_doosrel()`
- `procfs_doproccmdline()`
- `procfs_doprocdbregs()`
- `procfs_doprocfile()`
- `procfs_doprocfpregs()`
- `procfs_doprocmap()`
- `procfs_doprocmem()`
- `procfs_doprocnote()`
- `procfs_doprocregs()`
- `procfs_doprocrlimit()`
- `procfs_doprocstatus()`
- `procfs_doproctype()`

Declared attribute callbacks:
- `procfs_attr_w()`
- `procfs_attr_rw()`
- `procfs_attr_all_rx()`

Declared visibility callbacks:
- `procfs_notsystem()`
- `procfs_candebug()`

## Integration Points

This header depends on pseudofs callback macros such as `PFS_FILL_ARGS`, `PFS_ATTR_ARGS`, and `PFS_VIS_ARGS`, so it is included after pseudofs declarations by implementation files.

## Risks and Review Notes

The header is intentionally minimal and kernel-guarded. ABI/API coupling is mostly by callback signature; any pseudofs callback signature change would require coordinated updates here and in all procfs content files.
