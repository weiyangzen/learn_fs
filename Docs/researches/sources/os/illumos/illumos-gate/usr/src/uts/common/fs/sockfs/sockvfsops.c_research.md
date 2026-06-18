# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockvfsops.c

## Purpose
Provides the loadable filesystem module wrapper and minimal VFS operation support for `sockfs`.

## Key Elements
Registers `sockfs` through a `vfsdef_t` whose init function is `sockinit` and whose flags include `VSW_ZMOUNT`. `_init` creates a zone key so sockfs per-zone kstats are initialized and finalized for every zone, then installs the filesystem module. If module installation fails, the zone key is deleted. `_info` delegates to `mod_info`. `_fini` always returns `EBUSY`; sockfs is not unloadable.

`sockfs_statvfs` fills a token `statvfs64` response: zeroes the structure, sets `f_bsize` to `PAGESIZE`, derives `f_fsid` from `vfs_dev`, and sets `f_basetype` to `sockfs`.

## Dependencies
Uses illumos module, VFS, vnode, STREAMS, socket, zone, and kstat hooks. The real sockfs initialization is supplied by `sockinit` elsewhere.

## Behavior/Risks
This file intentionally exposes little filesystem capacity information. Module unload is disabled, so any future unload support would need to add real cleanup for the zone key and sockfs global state.
