# File Research: sources/os/linux/linux-stable/fs/ext4/truncate.h

## Purpose

`truncate.h` contains two small inline helpers shared by ext4 truncate/write-failure paths.

## Functions

- `ext4_truncate_failed_write(struct inode *inode)`
  - Handles cleanup after a write allocated blocks that were not ultimately used.
  - Takes the file mapping invalidate lock.
  - Truncates page cache back to `inode->i_size`.
  - Calls `ext4_truncate()` to remove blocks beyond the current size.
  - Releases the invalidate lock.
  - It intentionally skips `ext4_break_layouts()` because the blocks being removed were never visible to userspace.

- `ext4_blocks_for_truncate(struct inode *inode)`
  - Estimates journal transaction credits needed for the next truncate chunk.
  - Starts from `inode->i_blocks` converted from 512-byte sectors to filesystem blocks.
  - Floors the estimate at 2 blocks to survive corrupt but regular-looking inodes with nonsensical `i_blocks`.
  - Caps the chunk at `EXT4_MAX_TRANS_DATA` to avoid overflowing the journal.
  - Returns `EXT4_DATA_TRANS_BLOCKS(inode->i_sb) + needed`.

## Integration Points

These helpers are used by ext4 write and truncate paths that need to clean up partially allocated blocks or bound truncate transaction size. They depend on VFS page-cache invalidation, ext4 block truncation, and ext4 journal credit macros.

## Edge Cases

- The transaction sizing helper is corruption-tolerant: it tries to avoid kernel panics when on-disk `i_blocks` is bad.
- The failed-write cleanup assumes the discarded allocations were not user-visible, allowing a narrower cleanup path than normal truncate.
