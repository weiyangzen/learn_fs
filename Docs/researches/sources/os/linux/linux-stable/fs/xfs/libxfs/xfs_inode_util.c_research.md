# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_util.c

## Role
`xfs_inode_util.c` provides inode flag conversion, inode creation initialization, parent-to-child flag inheritance, project id inheritance, unlinked-list maintenance, link count updates, and inode uninitialization/freeing.

## Main Responsibilities
- Convert between userspace `FS_XFLAG_*` flags and on-disk `di_flags`/`di_flags2`.
- Initialize new inodes with correct ownership, mode, link count, timestamps, fork format, inherited flags, project id, and optional attr fork.
- Maintain per-AG on-disk unlinked inode hash chains plus in-core backreferences.
- Increment/decrement link counts and move zero-link inodes to or from AGI unlinked lists.
- Free an inode from allocation metadata and reset the in-core inode to an unallocated state.

## Important Functions
- `xfs_flags2diflags`, `xfs_flags2diflags2`, and `xfs_ip2xflags` translate between ioctl-visible flags and inode disk flags.
- `xfs_get_initial_prid` inherits project id only when the parent has `PROJINHERIT`.
- `xfs_inode_inherit_flags` and `xfs_inode_inherit_flags2` propagate realtime, extent-size, project, DAX, CoW extent-size, and metadata flags while clearing invalid inherited hints.
- `xfs_icreate_want_attrfork` pre-creates an attr fork when requested or when parent pointers require one.
- `xfs_inode_init` performs initial inode setup and logs the core/dev fields.
- `xfs_iunlink_update_bucket`, `xfs_iunlink_insert_inode`, and `xfs_iunlink` insert zero-link inodes into the AGI unlinked bucket chain.
- `xfs_iunlink_remove_inode` and `xfs_iunlink_remove` remove inodes from the unlinked chain, updating either the AGI bucket or the previous cached inode.
- `xfs_droplink` decrements link count, handles underflow by pinning the count, logs the inode, and inserts into unlinked lists at zero.
- `xfs_bumplink` increments link count, pins at overflow, and logs the inode.
- `xfs_inode_uninit` frees allocation metadata first, removes from unlinked list, clears local data, resets mode/flags/fork state, bumps generation, and logs the core.

## Data and Invariants
- Unlinked-list updates are serialized by the AGI buffer lock.
- In-core backreferences avoid scanning singly linked AGI chains when removing an inode.
- Inodes on unlinked lists must have VFS references, allowing lockless inode cache lookups for backreference updates.
- `O_TMPFILE` and zero-link files are kept reachable through AGI unlinked buckets until inactive/free time.
- Metadata children inherit the metadata flag from metadata directories.

## Error Handling and Corruption Response
- Invalid AGI bucket pointers or self-referential list entries mark the AGI sick and return `-EFSCORRUPTED`.
- Missing cached next inodes during unlinked updates trigger reload helpers; missing previous inodes during removal marks the current inode core sick.
- Link count underflow/overflow is rate-limited and pinned to avoid wrapping.

## Dependencies
This file depends on inode allocation/freeing, AGI reads, iunlink item logging, transaction timestamp logging, quota/project id policy, bmap hint validators, and health reporting.

## Research Notes
The most important design point is the two-layer unlinked-list model: persistent AGI singly linked buckets for crash consistency, plus in-core backreferences for scalable removal while the AGI lock serializes updates.
