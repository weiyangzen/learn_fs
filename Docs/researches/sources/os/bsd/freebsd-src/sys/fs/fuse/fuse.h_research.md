# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse.h

## Purpose
Provides top-level FUSE filesystem declarations, timeout constants, sysctl declarations, locking macros, and init/destroy prototypes.

## Main Elements
- Includes the FUSE kernel protocol header.
- Defines default, minimum, and maximum daemon timeout constants.
- Declares FUSE sysctl nodes for global settings and stats.
- Declares global `fuse_mtx` and wraps it with `FUSE_LOCK()`/`FUSE_UNLOCK()`.
- Defines `RECTIFY_TDCR()` to default missing thread/credential pointers.
- Provides mutex wrapper macros.
- Declares IPC and device init/destroy entry points.

## Dependencies And Integration
Included throughout FreeBSD fusefs implementation. It centralizes global locking and module lifecycle hooks used by device and IPC layers.

## Risk Notes
This header is small but broad. Changes to global lock wrappers or daemon timeout constants affect many FUSE request paths.
