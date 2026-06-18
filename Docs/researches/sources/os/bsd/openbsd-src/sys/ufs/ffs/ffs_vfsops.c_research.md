# File Research: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_vfsops.c

Implements FFS VFS operations: mount, reload, validation, sync, vnode lookup, file handles, superblock updates, initialization, and sysctl.

Key entry points:
- `ffs_vfsops` registers mount, unmount, statfs, sync, vget, fh conversion, init, sysctl, and export checks.
- `ffs_vtbl` binds UFS inode operation hooks to FFS implementations.
- `ffs_checkrange()` validates inode numbers and UFS2 lazy inode initialization for NFS file handles.
- `ffs_mountroot()`, `ffs_mount()`, and `ffs_mountfs()` attach filesystems.
- `ffs_reload()` refreshes read-only mounts after fsck.
- `ffs_validate()` checks superblock sanity.
- `ffs_oldfscompat()`, `ffs1_compat_read()`, and `ffs1_compat_write()` handle old UFS1 layout compatibility.
- `ffs_unmount()` flushes, marks clean, closes the device, and frees mount allocations.
- `ffs_flushfiles()` handles quota/system vnode flushing.
- `ffs_statfs()` reports block and inode availability.
- `ffs_sync()` flushes dirty vnodes, quotas, device buffers, and superblock state.
- `ffs_vget()` loads UFS1/UFS2 dinodes and initializes vnodes.
- `ffs_fhtovp()` and `ffs_vptofh()` convert NFS file handles.
- `ffs_sbupdate()` writes summary blocks then the superblock.
- `ffs_init()` initializes inode/dinode pools once.
- `ffs_sysctl()` exposes bounded dirhash sysctls when enabled.

Important behavior:
- Mount scans all known superblock locations and avoids interpreting an FFS1 superblock at the UFS2 location.
- Read-write mount is denied for unclean filesystems unless forced.
- Writable mounts allocate `fs_contigdirs`, set `fs_clean = 0`, and write the dirty superblock.
- `ffs_reload()` reuses existing pointer fields, reloads cylinder summaries, resets cluster knowledge, then reloads active vnodes.
- `ffs_sync()` can temporarily force clean/dirty superblock state during stall sync, then restores in-memory state.
- `ffs_sbupdate()` writes cylinder summaries first and avoids writing a clean superblock if summary writes failed.
- `ffs_vget()` sets generation numbers on old filesystems and supports UFS1 old uid/gid compatibility.

Dependencies:
- Uses generic UFS operations, quota code, dirhash sysctls, buffer cache, vnode iteration, FFS allocation/inode helpers, and `ffs_tables.c`.

Watch points:
- Clean/dirty handling is conservative and intentionally refuses normal read-write mount of unclean filesystems.
- `ffs_sync()` panics if modified filesystem state exists while mounted read-only.
- Many old-format compatibility paths are marked with `XXX`, but are still part of the mount/write path.
