# File Research: sources/os/bsd/freebsd-src/sys/fs/autofs/autofs_vfsops.c

## Purpose
VFS operation implementation for mounting, unmounting, rooting, and statfs on autofs mounts.

## Main Elements
- Accepts mount options `from`, `master_options`, `master_prefix`, and required `fspath`.
- Update mounts flush autofs cache.
- New mounts allocate `struct autofs_mount`, copy map/prefix/options/mountpoint data, initialize lock and root node, set lookup-shared flag, and set mounted-from text.
- `autofs_unmount()` flushes vnodes, completes outstanding requests for the mount with `ENXIO`, waits for them to drain, then deletes the node tree.
- `autofs_root()` returns the root autofs vnode.
- `autofs_statfs()` reports synthetic zero-capacity filesystem statistics.
- Registers `VFS_SET(..., autofs, VFCF_SYNTHETIC | VFCF_NETWORK)`.

## Dependencies And Integration
Uses autofs node helpers, VFS mount option APIs, vnode flushing, and module registration.

## Risk Notes
Unmount must prevent new triggers, wake existing trigger waiters, and delete nodes only after vnodes are gone.
