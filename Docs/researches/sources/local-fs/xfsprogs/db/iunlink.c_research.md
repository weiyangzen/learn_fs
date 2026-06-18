# File Research: sources/local-fs/xfsprogs/db/iunlink.c

## Purpose
Implements unlinked-inode list inspection and an expert-mode command to create unlinked tmpfile-style inodes.

## Main Interfaces
- `iunlink_init()` registers `dump_iunlinked` for all modes and `iunlink` in expert mode.
- `dump_iunlinked [-a agno] [-b bucket] [-q] [-v]` dumps AGI unlinked buckets and chain contents.
- `iunlink [-n nr]` allocates one or more unlinkable temporary regular inodes and links them into the AG unlinked list.

## Control Flow
Dumping reads each selected AGI, prints bucket heads, follows `di_next_unlinked` by igetting each inode, and optionally prints data/realtime block counts. Creation allocates a create-tmpfile transaction, calls `libxfs_dialloc`, `libxfs_icreate`, and `libxfs_iunlink`, commits, and reports the new inode.

## Dependencies
Uses AGI reads, inode iget/imap, extent iteration for realtime block accounting, libxfs transaction/create/iunlink helpers, and xfs_db output.

## Risks And Invariants
- Bucket values are bounded by `XFS_AGI_UNLINKED_BUCKETS`.
- Verbose block counting reads data fork extents for realtime inodes.
- Creation is expert-only and mutates filesystem metadata.
