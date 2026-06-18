# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtrmap_btree.c

## Purpose

`xfs_rtrmap_btree.c` implements the realtime reverse mapping btree. This inode-rooted overlapping btree tracks ownership of realtime device extents, supports staged and optional in-memory forms, and provides conversion between metadata inode roots and generic btree blocks.

## Main Content

- Defines a kmem cache for realtime rmap btree cursors.
- Implements btree cursor operations:
  - Cursor duplication.
  - Min/max record calculations.
  - On-disk root max records.
  - Key/high-key initialization.
  - Record initialization from cursor state.
  - Pointer initialization.
  - Three-part key comparison: start block, owner, offset.
- Masks unwritten state from rmap key comparisons because written/unwritten is a record attribute, not a key discriminator.
- Implements verifier and buffer ops for realtime rmap btree blocks.
- Defines `xfs_rtrmapbt_ops` as an overlapping inode-rooted btree.
- Provides optional `CONFIG_XFS_BTREE_IN_MEM` in-memory rtrmap btree verifier, buffer ops, btree ops, cursor creation, and initialization.
- Commits staged btree roots by replacing the metadata inode’s real data fork.
- Computes record capacity, maximum on-disk height, mount maximum height, btree size, and reserve size.
- Converts root blocks between on-disk dinode root format and in-memory generic btree block format.
- Loads and flushes realtime rmap metadata inode roots.
- Creates empty realtime rmap metadata inode roots.
- Initializes the rmap record for a realtime superblock reservation.
- Reads the highest tracked RT group block number from the root high key.

## Key Interfaces and Invariants

- Realtime rmap btrees require rmapbt support; growfs can create rmap inodes before an RT section is attached.
- The btree is overlapping, so internal nodes store low and high keys.
- Unwritten extent state is masked out of key comparisons.
- Reflink can create theoretically huge rmap record counts, so max-level calculation for rtreflink considers data-device space rather than record count alone.
- Reserve sizing keeps at least 1% of the RT group or enough for one block per record.
- Staged root commit sets the metadata inode project id to the RT group number.

## Dependencies

Depends on generic btree/staging APIs, optional in-memory btree APIs, realtime group state, rmap encoding, metadata inode allocation, health masks, buffer CRC helpers, and transaction/inode fork helpers.
