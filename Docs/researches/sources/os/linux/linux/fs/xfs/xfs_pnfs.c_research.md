# File Research: sources/os/linux/linux/fs/xfs/xfs_pnfs.c

## Purpose

`xfs_pnfs.c` implements XFS support for pNFS block layouts through `exportfs_block_ops`. It maps file byte ranges to block-device layouts for NFS clients, commits client-written blocks, and coordinates layout recalls with local filesystem operations.

## Main Responsibilities

- Break outstanding leased pNFS layouts before local operations that remove blocks.
- Advertise supported block layout ID modes.
- Export a stable filesystem UUID and its superblock offset.
- Map file ranges to iomaps for pNFS clients.
- Allocate blocks for pNFS writes and make the allocation durable before handing it out.
- Commit client-written blocks by invalidating cache, converting unwritten extents, updating timestamps, and optionally extending file size.

## Important Functions

- `xfs_break_leased_layouts`: loops on `break_layout`; if blocking is needed, drops/reacquires XFS IOLOCK exclusively and reports that it unlocked.
- `xfs_fs_layouts_supported`: advertises in-band ID support and optional out-of-band ID support from the block device.
- `xfs_fs_get_uuid`: returns the filesystem UUID and offset of `sb_uuid` in the disk superblock.
- `xfs_fs_map_update_inode`: strips SUID/SGID as needed, updates mtime/ctime, marks preallocation, logs inode core, and commits.
- `xfs_fs_map_blocks`: validates export constraints, flushes and invalidates pagecache, maps or allocates extents, logs durability, converts to iomap, and returns device generation.
- `xfs_pnfs_validate_isize`: ensures a proposed size extension lands in a valid allocated written block.
- `xfs_fs_commit_blocks`: invalidates affected cache, converts unwritten extents, updates timestamps and size, and commits synchronously.

## Export Constraints

The mapping path rejects:

- shutdown filesystems,
- realtime inodes because the realtime device lacks a UUID export identity,
- reflink inodes because Linux pNFS block layout does not implement the needed reflink semantics,
- offsets beyond allowed file size limits.

## Locking and Consistency

`xfs_fs_map_blocks` takes `XFS_IOLOCK_EXCL`, flushes dirty pagecache, invalidates cached pages, reads or allocates mappings under data-map locks, and forces the log for newly allocated write layouts. `xfs_fs_commit_blocks` also takes `XFS_IOLOCK_EXCL` while converting extents and updating inode metadata.

## Exported Interface

The file defines `xfs_export_block_ops` with:

- `.layouts_supported`
- `.get_uuid`
- `.map_blocks`
- `.commit_blocks`
