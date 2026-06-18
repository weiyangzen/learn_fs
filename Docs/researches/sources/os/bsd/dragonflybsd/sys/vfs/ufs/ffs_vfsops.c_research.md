# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_vfsops.c

DragonFly VFS operations for mounting, unmounting, syncing, statfs, vnode lookup, file handles, initialization, and superblock updates for UFS/FFS.

Key responsibilities:
- Registers the `ufs` VFS with mount, unmount, root, quota, statfs, sync, vget, file-handle conversion, export checking, and init handlers.
- Implements root mount, new mount, and update/remount handling in `ffs_mount()`, including user argument copyin, device lookup, permission checks, read-only/read-write transitions, export updates, clean-bit handling, and softdep activation.
- Implements `ffs_reload()` for read-only filesystem reload after fsck, invalidating device metadata, rereading the superblock and summary info, and refreshing active inode contents.
- Implements `ffs_mountfs()` common mount setup: validates the block device and superblock, opens the device, copies the superblock, reads summary blocks, allocates per-mount summary/cluster/contiguous-directory state, initializes `ufsmount`, sets vnode ops, initializes inode hash, handles old filesystem compatibility, caps max file size for VM object limits, and marks writable filesystems dirty.
- Implements `ffs_unmount()` with softdep-aware flushing, clean superblock update, device buffer invalidation, device close, inode hash teardown, and memory cleanup.
- Implements `ffs_flushfiles()` with quota shutdown support, vnode flushing, and device metadata fsync.
- Implements `ffs_statfs()` from in-memory superblock counters and `freespace()`.
- Implements `ffs_sync()` to scan dirty vnodes, fsync modified files, flush device metadata, sync quotas, and write the superblock.
- Implements `ffs_vget()` to find or instantiate in-core inodes, read dinodes from disk, apply softdep effective link counts, initialize vnode type/ops, handle aliases, set generation numbers, and preserve old inode-format uid/gid compatibility.
- Implements NFS file-handle conversion with inode range validation and generation numbers.
- Implements `ffs_sbupdate()` to write summary information and the superblock, including compatibility transforms for old FFS formats.

Dependencies:
- Uses DragonFly VFS, vnode, buffer cache, device, nlookup, disk, VM, quota, and mount infrastructure.
- Depends on local headers `quota.h`, `ufsmount.h`, `inode.h`, `ufs_extern.h`, `fs.h`, and `ffs_extern.h`.
- Calls softdep entry points when `MNT_SOFTDEP` or `FS_DOSOFTDEP` is active.

Notable risks:
- Mount clean-bit policy rejects read-write mounts of unclean filesystems unless forced or read-only; forced dirty mounts only warn.
- Soft updates is explicitly incompatible with async mounts, so softdep mount/update clears `MNT_ASYNC`.
- Device vnode identity during update is handled carefully across devfs aliases; wrong matching can reject updates or reuse the existing device vnode.
- Error cleanup in `ffs_mountfs()` must release buffers, close the device, uninitialize inode hash state, and free mount allocations in the correct order.
- `ffs_reload()` assumes read-only state and a VMIO-capable device vnode; violations panic.
- Several compatibility sections preserve old 4.2/4.4 FFS layout behavior, increasing risk around superblock field ordering and max-file-size handling.
