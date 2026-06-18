# File Research: sources/os/linux/linux/fs/xfs/xfs_itable.c

## Role
Implements bulk inode stat and inode-number table queries. It walks allocated inode records through `xfs_iwalk`/`xfs_inobt_walk`, formats internal v5 bulk result structures, and lets ioctl callers provide output formatters for legacy or native userspace ABI layouts.

## Main Structures and Entry Points
- `xfs_bulkstat_one` returns one inode's bulkstat data.
- `xfs_bulkstat` walks allocated inodes starting from a cursor and formats multiple records.
- `xfs_bulkstat_to_bstat` converts v5 `xfs_bulkstat` to legacy `xfs_bstat`.
- `xfs_inumbers` walks inode btree records and formats inode allocation groups.
- `xfs_inumbers_to_inogrp` converts v5 `xfs_inumbers` to legacy `xfs_inogrp`.
- Internal `xfs_bulkstat_one_int` gathers metadata for one inode.

## Behavior
Bulkstat uses `xfs_iget` with `XFS_IGET_DONTCACHE | XFS_IGET_UNTRUSTED`, skips missing/freed/internal private inodes, reloads incomplete unlinked-list state when needed, maps inode uid/gid through the mount idmap, fills size, timestamps, generation, mode, xflags, extent counts, fork offsets, health state, v3 birth time and CoW extent size, device fields, block size, and block counts. Metadata directory files can be minimally exposed when the request sets `XFS_IBULK_METADIR`.

The cursor `breq->startino` advances past skipped or successfully emitted inodes so userspace can resume. Formatter `-ECANCELED` means the caller's output buffer filled; the public functions hide that from userspace when records were produced.

Inumbers formats inobt records as start inode, allocated count, allocation mask, and version. It similarly advances the cursor by one inode chunk and clears errors when at least one record was returned.

## Interactions
Called by native and compat ioctl code. Relies on `xfs_iwalk` for allocated inode iteration, `xfs_inobt_walk` for raw inode btree record iteration, inode cache lookup, health reporting, unlinked-list reload, and empty transactions for recursive buffer locking/cycle detection.

## Invariants and Error Handling
- Bulkstat is rejected inside idmapped mounts because the exported ABI cannot represent that safely.
- Start inode values that do not map into the filesystem are treated as already done.
- Private inodes and superblock inodes are not leaked through normal bulkstat.
- Errors after some output records are suppressed so the next call resumes at the problematic cursor and can report the error without partial output.
