# File Research: sources/os/linux/linux-stable/fs/ext4/migrate.c

## Purpose

Implements ext4 inode block-mapping migration between legacy indirect-block mappings and extent mappings. It supports full indirect-to-extent migration via a temporary inode and a restricted extent-to-indirect migration for simple inline-root extent layouts.

## Main Responsibilities

- Walk direct, indirect, double-indirect, and triple-indirect block maps and coalesce contiguous physical blocks into extents.
- Insert generated extents into a temporary extent inode while managing journal credits.
- Swap generated extent metadata into the original inode atomically enough to detect concurrent allocations.
- Free obsolete indirect metadata blocks after a successful indirect-to-extent conversion.
- Free temporary extent metadata after failures.
- Convert a simple extent inode back to direct block pointers when supported.
- Mark migration transactions fast-commit ineligible because mapping-layout rewrites are not represented in the fast-commit log.

## Key Operations

- `finish_range()` converts the currently accumulated contiguous logical/physical range into an `ext4_extent` and inserts it into the temporary inode's extent tree.
- `update_extent_range()` extends the current migration run when logical and physical blocks remain contiguous, otherwise flushes the previous run and starts a new one.
- `update_ind_extent_range()`, `update_dind_extent_range()`, and `update_tind_extent_range()` read indirect blocks at each depth and feed referenced data blocks into the extent-run builder while advancing logical block positions over holes.
- `free_dind_blocks()`, `free_tind_blocks()`, and `free_ind_block()` recursively free indirect metadata blocks with journal credit extension and revoke accounting.
- `ext4_ext_swap_inode_data()` verifies the migration flag, clears it, sets `EXT4_INODE_EXTENTS`, copies the temporary inode's extent-root data into the original inode, adjusts `i_blocks`, frees old indirect metadata, and marks the inode dirty.
- `free_ext_idx()` and `free_ext_block()` recursively free extent metadata allocated to the temporary inode when migration cannot be completed.
- `ext4_ext_migrate()` is the main indirect-to-extent conversion path. It rejects unsupported inodes, creates a hidden temporary inode with matching checksum seed, builds an extent tree from old block pointers, swaps mappings on success, and resets/drops the temporary inode.
- `ext4_ind_migrate()` converts only extent inodes whose entire mapping is one root-level initialized extent fitting within the direct block array; it rejects bigalloc, deep extent trees, multiple extents, large physical block files, and extents beyond `EXT4_NDIR_BLOCKS`.

## Dependencies

- Includes `ext4_jbd2.h` and `ext4_extents.h`.
- Depends on ext4 journal credit helpers, extent tree insertion/checking/initialization, inode allocation, writepages exclusion, block bitmap freeing through `ext4_free_blocks()`, inode flags/state, quota ownership, and fast-commit eligibility marking.

## Important Invariants

- Indirect-to-extent migration uses `EXT4_STATE_EXT_MIGRATE` to detect block allocations racing with migration. If another allocation clears the state, swap fails with `-EAGAIN`.
- The temporary inode uses the original inode's checksum seed while building extent metadata so the metadata checksums remain valid after the root extent data is copied.
- The original inode is only marked extent-based after generated extent metadata is ready and the migration state check succeeds.
- Obsolete indirect metadata is freed after the new extent root is installed; temporary extent metadata is freed on failure.
- Extent-to-indirect migration is intentionally narrow: depth zero, at most one extent, no bigalloc, no blocks beyond direct pointer capacity.

## Research Notes

The file is a bridge between ext4's old indirect mapping format and extent format. The indirect-to-extent path avoids in-place transformation by building the target extent tree in a temporary inode, then swapping the root mapping data into the real inode under `i_data_sem`. That design keeps extent construction isolated but requires careful cleanup and journaling around both old indirect metadata and temporary extent metadata.
