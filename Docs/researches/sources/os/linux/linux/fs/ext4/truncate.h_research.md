# File Research: sources/os/linux/linux/fs/ext4/truncate.h

## Purpose
Defines small inline helpers shared by ext4 truncate paths.

## Main Elements
- `ext4_truncate_failed_write()`: invalidates pagecache beyond the current inode size and calls `ext4_truncate()` after a failed write allocation path.
- `ext4_blocks_for_truncate()`: estimates transaction credits needed for a truncate chunk from `i_blocks`, clamps suspiciously small values upward, and caps the transaction at `EXT4_MAX_TRANS_DATA`.

## Dependencies And Integration
Uses the inode mapping invalidate lock, pagecache truncation helpers, `ext4_truncate()`, and ext4 transaction credit macros. Included by truncate/write paths that need common cleanup and credit sizing.

## Behavioral Notes
Failed-write truncation skips `ext4_break_layouts()` because the blocks being discarded were never visible to userspace. Credit sizing is intentionally defensive against corrupt inodes whose `i_blocks` value is nonsensical.

## Risk Notes
The helpers protect against both stale buffer mappings after failed writes and oversized journal transactions during truncation. Incorrect credit estimates here could cause journal credit exhaustion or unnecessary transaction splitting.
