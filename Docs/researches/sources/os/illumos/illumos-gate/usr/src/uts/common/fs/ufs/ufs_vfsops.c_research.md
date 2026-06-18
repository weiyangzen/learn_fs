# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_vfsops.c

## Overview
`ufs_vfsops.c` implements the UFS VFS module wrapper and filesystem lifecycle operations: mount, remount, root mount/unmount, unmount, root lookup, statvfs, sync, vget, syncfs, and VFS/vnode operation registration. It is the central integration point between UFS on-disk state, mount options, logging, lockfs, quotas, snapshots, background threads, and the illumos VFS framework.

## Main Responsibilities
- Register the UFS filesystem module and VFS operations.
- Parse and apply UFS mount options including logging, largefiles, direct I/O, xattrs, noatime/deferred atime, and onerror policy.
- Validate mount devices and UFS superblock magic/version/geometry.
- Mount ordinary filesystems and the root filesystem.
- Remount read-only root or mounted filesystems read-write.
- Initialize `ufsvfs`, root inode, lockfs state, summary info, logging state, and background workers.
- Unmount cleanly or forcibly with lockfs coordination.
- Report filesystem statistics and adjust for delayed delete accounting.
- Sync all UFS filesystems or a single mounted instance.
- Resolve file handles for NFS-style `VFS_VGET`.

## Mount and Remount Flow
- `ufs_mount()` checks mount privilege, validates the mount point, copies `ufs_args`, resolves the special vnode or lofi backing vnode, checks access, prevents duplicate device mounts, handles tape read-only policy, and delegates to `mountfs()`.
- `ufs_mountroot()` handles root init, root remount, and root unmount; root unmount flushes logs/summary info when possible and closes the root device.
- `mountfs()` opens the device for root init, invalidates block-device pages, reads and validates the superblock, allocates `ufsvfs`, links it into `ufs_instances`, initializes delete/reclaim queues, snarfes logging state, copies the superblock into a native-sized buffer, reads summary info, initializes lockfs, gets the root inode, computes geometry/cache tunables, starts delete/reclaim threads when needed, writes mount-time superblock state, and initializes fix-on-panic policy.
- `remountfs()` updates mount options, rejects read-only remount-to-readonly, quiesces the filesystem, rereads and validates the superblock, restarts log rolling, restores summary info, switches to read-write state, starts workers, and writes the superblock.

## Unmount Flow
- `ufs_unmount()` supports forced unmount by marking `VFS_UNMOUNTED`, suspending delete work, hard-locking/quiescing/flushing through lockfs, and then continuing cleanup.
- It rejects unmount if lockfs counts, falloc counts, or soft locks indicate active users.
- Normal unmount flushes pending operations; hard/error-locked unmount skips some inode-cache checks.
- It deletes snapshots during hard/error-locked forced unmounts, otherwise snapshots make unmount fail with `EBUSY`.
- It closes quotas, invalidates dquots, drains delete and idle queues, invalidates/removes all cached inodes, flushes shadow inode cache, exits worker threads, writes final clean/log state, commits outstanding transactions, releases logging state, updates fix-on-panic bookkeeping, frees summary info, closes device vnode, removes the instance, and either frees or defers freeing `ufsvfs`.
- On unmount failure, it reopens operations, resumes workers, marks the filesystem mounted again, triggers transaction error handling, and may force summary-info logging for `/usr`.

## Sync and Stat Operations
- `ufs_statvfs()` validates the superblock, reports block/file counts, adjusts free space for delayed delete queue entries on logging filesystems, computes available blocks after minfree, and fills base type, flags, and name length.
- `ufs_sync()` handles global sync via `ufs_update()` or single-filesystem sync: write modified superblock, scan inodes, flush buffers, and commit async transactions.
- `sbupdate()` writes summary information and the superblock for non-logging filesystems, or delegates to `ufs_sbwrite()` for logging filesystems.
- `ufs_syncfs()` maps syncfs to `ufs_fioffs()` and rejects nonzero flags.

## VGET and Root
- `ufs_root()` returns a held root vnode or `EIO` after forced unmount.
- `ufs_vget()` rejects unmounted filesystems, trims the idle queue before lockfs entry when needed, uses lockfs begin/end around `ufs_iget()`, and validates generation, mode, and link count before returning a vnode.
- Deleted, freed, stale, or generation-mismatched handles return `EINVAL`.

## Module Registration
- `_init()` creates thread-specific-data keys for lockfs and snapshot throttling, then installs the filesystem module.
- `_fini()` returns `EBUSY`, making the module effectively non-unloadable.
- `ufsinit()` registers VFS ops, vnode ops, stores the filesystem type, and initializes inode support.

## Locking and Safety
- Mount and unmount require VFS locks at key lifecycle boundaries.
- `ufsvfs_mutex` protects global instance list operations.
- `ufs_scan_lock` prevents races among inode scans, sync, and unmount.
- `ul_lock`, `ufs_quiesce_pend`, and lockfs state coordinate quiesce/freeze/thaw behavior.
- Forced-unmount handling can defer freeing `ufsvfs` to avoid sleepers in lockfs code dereferencing freed state.
- Mount failure cleanup removes partially cached root inodes and waits briefly for stray references before marking stale and leaking rather than freeing unsafely.

## Research Notes
This is the highest-level UFS integration file. Its main correctness risks are lifecycle races during failed mount and forced unmount, log replay/summary-info state transitions, worker-thread coordination, snapshot ownership during unmount, and consistency between mount options and superblock clean/log flags.
