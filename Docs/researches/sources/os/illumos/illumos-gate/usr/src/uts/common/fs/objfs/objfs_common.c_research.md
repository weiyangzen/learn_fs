# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/objfs/objfs_common.c

## Purpose
Provides common objfs vnode helper routines shared by root, object-directory, and data-file nodes.

## Main Entry Points
- `objfs_dir_open()` permits directory opens only with `FOFFMAX` and rejects writable opens.
- `objfs_common_close()` is a no-op close callback for nodes needing no per-close cleanup.
- `objfs_dir_access()` denies directory write access and allows other access.
- `objfs_common_getattr()` fills common `vattr_t` fields such as owner, group, block size, block count, sequence, and fsid.
- `objfs_nobjs()` counts currently loaded kernel modules.

## Internal Mechanics
`objfs_nobjs()` walks the global `modules` circular list under `mod_lock` and counts `mod_loaded` entries. Attribute helpers treat objfs as read-only, root-owned, and device-block-sized.

## Dependencies
Uses objfs internal headers, generic file/vnode types, module control list state, `mod_lock`, and kernel block-size helpers.

## Risks and Notes
The loaded-object count is dynamic and only a snapshot under `mod_lock`; directory link counts/statvfs values can change as modules load or unload.
