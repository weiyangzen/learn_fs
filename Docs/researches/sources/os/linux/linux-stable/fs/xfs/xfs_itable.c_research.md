# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_itable.c

This file implements XFS bulk inode reporting for userspace, using inode btree walking to produce bulkstat and inumbers records.

Bulkstat:
- `xfs_bulkstat_one_int` loads an inode with `xfs_iget`, fills `struct xfs_bulkstat`, and invokes a caller-provided formatter.
- It skips missing, invalid, private, and superblock-reserved inodes unless metadata-directory reporting is explicitly requested.
- It reloads incomplete unlinked-list state before allowing inodegc-sensitive paths to proceed.
- It maps uid/gid through the request idmap and superblock user namespace.
- It reports size, times, generation, mode, xflags, extent size, extent counts, health, attr extent counts, fork offset, v5 version, birth time, CoW extent size, rdev, block size, and block count.
- `xfs_bulkstat_one` reports one inode.
- `xfs_bulkstat` walks allocated inodes using `xfs_iwalk`.

Legacy conversion:
- `xfs_bulkstat_to_bstat` converts v5 `xfs_bulkstat` to legacy `xfs_bstat`, including byte conversion for extent size and CoW extent size.

Inumbers:
- `xfs_inumbers_walk` converts inode btree records into `struct xfs_inumbers`, including start inode, allocated count, allocation mask, and version.
- `xfs_inumbers` walks inode btree records using `xfs_inobt_walk`.
- `xfs_inumbers_to_inogrp` converts v5 inumbers to legacy `xfs_inogrp`.

Cursor behavior:
- `breq->startino` is used as the userspace cursor and advanced whenever the current inode or inode chunk can be skipped or reported.
- `-ECANCELED` is used internally to stop iteration when the userspace output buffer is full; callers translate it as success if records were produced.

Validation and limits:
- Bulkstat rejects idmapped mounts except `nop_mnt_idmap`.
- `xfs_bulkstat_already_done` returns early if the starting inode is beyond the filesystem or cannot map cleanly to AG/agino coordinates.
- Empty transactions are used for recursive buffer locking and cycle detection while walking inode btrees.

Integration:
- Called by native and compat ioctl paths.
- Depends on `xfs_iwalk.c` for iteration and `xfs_health` for inode health flags.
