# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/lofs/lofs_vfsops.c

## Role

Implements module linkage and VFS operations for LOFS. This file handles mounting, unmounting, root/stat/sync/vget operations, and registration of LOFS VFS and vnode operation tables.

## Major Responsibilities

- Defines the LOFS module wrapper and filesystem definition.
- Defines LOFS mount options: xattr/noxattr and sub/nosub.
- Implements `lo_mount()` to create a loopback mount over an existing path.
- Enforces mount permissions, overlay rules, zone/MAC policy, and inherited mount flags.
- Initializes per-mount `struct loinfo` and root lnode.
- Exposes VFS operations through `lofsinit()`.

## Key Functions

- `_init()`: Initializes LOFS subroutines and installs the module.
- `_fini()`: Returns `EBUSY`; LOFS is not unloadable.
- `_info()`: Module information.
- `lo_mount()`: Main mount implementation.
- `lo_unmount()`: Rejects forced unmount, requires only root lnode reference to remain, then releases it.
- `lo_root()`: Returns the LOFS root vnode, using `specvp()` for device special roots.
- `lo_statvfs()`: Delegates statvfs to the real root’s current VFS, which matters after forced unmount behavior in underlying filesystems.
- `lo_sync()`: No-op for general sync because LOFS has no own data.
- `lo_syncfs()`: Directed syncfs passes through to the real VFS.
- `lo_vget()`: Passes fid-to-vnode lookup to the underlying real VFS.
- `lo_freevfs()`: Destroys and frees `struct loinfo`.
- `lofsinit()`: Registers VFS ops and vnode ops, stores filesystem type.

## Mount Path Details

`lo_mount()` performs:

- Privilege check with `secpolicy_fs_mount()`.
- Overlay/busy checks on the mount point.
- Path lookup of `uap->spec` to get the real root vnode.
- Labeled-system policy for global-zone mounts, including read-only enforcement for read-down cases and special allowances for scratch zones and `NET_MAC_AWARE`.
- `VOP_ACCESS(realrootvp, 0, ...)` to trigger autofs if the source path is an autofs trigger.
- `traverse()` to mount the topmost filesystem after autofs resolution.
- `struct loinfo` allocation and setup.
- Inheritance of restrictive flags such as readonly, nosuid, nodevices, and nosetuid.
- Handling of permissive flags such as xattr and NBMAND using explicit deny flags.
- VFS feature propagation from real VFS to LOFS VFS.
- Hash-table initialization through `lsetup()`.
- Root vnode creation through `makelonode()`.

## Mount Options

- `MNTOPT_XATTR` / `MNTOPT_NOXATTR`: Controls extended attribute exposure.
- `MNTOPT_LOFS_SUB` / `MNTOPT_LOFS_NOSUB`: Controls whether LOFS traverses subordinate mounted filesystems during lookup.
- Standard mount options such as ro, nosuid, nodevices, nosetuid, nbmand/nonbmand are interpreted into LOFS inherited/denied VFS flags.

## Edge Cases and Semantics

- LOFS forbids forced unmount.
- A loopback mount over autofs performs access and traversal so the mounted target is the filesystem autofs resolves to, not the trigger node.
- Global-zone labeled mounts can be forced read-only to prevent write-up.
- `lo_root()` returns `specvp()` for device roots because the lnode table stores only LOFS nodes, not their specfs wrappers.
- `lo_statvfs()` intentionally avoids relying only on cached real VFS state so it can reflect forced-unmount dummy ops.
- Non-directory loopback roots use a one-bucket lnode hash table because they do not require broad directory traversal caching.

## Dependencies

Depends on `lofs_subr.c` for `lsetup()`, `ldestroy()`, `makelonode()`, and `lo_realvfs()`. It also uses common VFS registration APIs, `lookupname()`, `traverse()`, zone/label APIs, privilege policy, mount option helpers, and `lofs_vnops.c` vnode template.
