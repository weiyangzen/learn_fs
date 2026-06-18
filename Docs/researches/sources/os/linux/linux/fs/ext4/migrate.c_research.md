# File Research: sources/os/linux/linux/fs/ext4/migrate.c

## Purpose

Implements inode block mapping migration between legacy indirect block mapping and extent mapping.

It provides:
- `ext4_ext_migrate()`: converts an indirect-mapped inode to extents.
- `ext4_ind_migrate()`: converts a simple extent-mapped inode back to direct block pointers.

## Indirect to Extents

`ext4_ext_migrate()` converts a non-extent inode into extent format by building a temporary extent inode and swapping its extent tree into the original inode.

Flow:
1. Rejects unsupported cases:
   - filesystem lacks extents;
   - inode already uses extents;
   - inode has inline data;
   - fast symlink with no blocks.
2. Starts a migrate journal transaction and marks fast commit ineligible.
3. Creates a temporary hidden inode near the original inode’s group.
4. Copies checksum seed and size into the temporary inode.
5. Initializes the temp inode extent tree.
6. Sets `EXT4_STATE_EXT_MIGRATE` under `i_data_sem` to detect racing allocation.
7. Traverses original direct, indirect, double-indirect, and triple-indirect mappings.
8. Coalesces contiguous logical/physical ranges into extents with `update_extent_range()`.
9. Inserts extents into the temporary inode via `finish_range()`.
10. Swaps extent data into the original inode with `ext4_ext_swap_inode_data()`.
11. Frees old indirect metadata blocks.
12. Resets and drops the temporary inode.

## Traversal Helpers

- `update_extent_range()` maintains the currently coalesced logical/physical run.
- `finish_range()` inserts the accumulated range as an extent into the temp inode.
- `update_ind_extent_range()` scans one indirect block.
- `update_dind_extent_range()` scans a double-indirect block.
- `update_tind_extent_range()` scans a triple-indirect block.

Sparse holes advance `curr_block` without inserting extents.

## Freeing Old Metadata

- `free_ind_block()` frees indirect, double-indirect, and triple-indirect metadata roots.
- `free_dind_blocks()` frees indirect blocks beneath a double-indirect block, then the double-indirect block itself.
- `free_tind_blocks()` recursively frees double-indirect trees beneath a triple-indirect block, then the triple-indirect block.
- All metadata freeing uses journal credit extension and `ext4_free_blocks()` with metadata/forget flags.

## Swapping Data

`ext4_ext_swap_inode_data()`:
- Saves original indirect block roots.
- Takes `i_data_sem`.
- Verifies `EXT4_STATE_EXT_MIGRATE` is still set; if allocation raced, returns `-EAGAIN`.
- Sets `EXT4_INODE_EXTENTS`.
- Copies temp inode `i_data` into the original inode.
- Adds temp inode `i_blocks` for newly allocated extent metadata.
- Frees old indirect blocks and marks the inode dirty.

## Extents to Indirect

`ext4_ind_migrate()` only supports very simple extent files:
- filesystem must support extents;
- inode must currently use extents;
- bigalloc is rejected;
- delayed allocation is forced out first;
- extent tree must have depth 0 and at most one extent;
- extent must fit in direct blocks (`EXT4_NDIR_BLOCKS`).

It clears the extent flag, zeroes `i_data`, fills direct block entries from the single extent, and marks the inode dirty.

## Concurrency and Journaling

- Uses `ext4_writepages_down_write()`/`up_write()` around migrations.
- Uses `i_data_sem` to protect inode mapping mutation.
- Uses `EXT4_STATE_EXT_MIGRATE` to detect allocation races during indirect-to-extent conversion.
- Marks fast commit ineligible because mapping-layout rewrites are not represented in fast commit logs.
- Repeatedly ensures journal credits before extent insertion and metadata freeing.

## Error Handling

- On failed extent construction, frees temp extent metadata with `free_ext_block()`.
- On failed swap, frees temp extent metadata.
- Temporary inode is reset to size zero and `i_blocks = 0` before eviction.
- I/O errors from metadata block reads and journal credit failures propagate.

## Research Notes

This file is a conservative migration utility. The indirect-to-extent path handles full indirect trees, while the reverse migration intentionally supports only a shallow, single-extent direct-block-compatible case.
