# File Research: sources/os/linux/linux-stable/fs/ufs/inode.c

## Summary
Implements UFS inode block mapping, page-cache address-space operations, inode read/write conversion for UFS1 and UFS2, eviction, truncate/freeing of direct and indirect blocks, and file setattr/truncate handling.

## Main Responsibilities
- Maps logical fragments through direct, single-, double-, and triple-indirect pointers.
- Allocates fragments/blocks on write through `ufs_getfrag_block()`.
- Extends partial tail fragments and creates indirect blocks as needed.
- Provides read/writepage, write_begin/write_end, bmap, and buffer migration address-space operations.
- Assigns VFS inode/file/address-space operations based on file type.
- Reads UFS1 and UFS2 on-disk inodes into Linux inode state.
- Writes Linux inode state back to UFS1/UFS2 on-disk inode formats.
- Evicts deleted inodes, truncates data blocks, clears on-disk inode state, and frees inode bitmap entries.
- Frees direct, indirect, double-indirect, and triple-indirect block trees during truncation.
- Handles `setattr()` size changes via UFS truncate.

## Important Behavior
Block pointer reads use a seqlock (`meta_lock`) to retry if metadata changes during traversal. Allocation and truncation serialize through `truncate_mutex`.

Fast symlinks are stored in the inode data area when `i_blocks == 0`; other symlinks use page-cache symlink operations.

`ufs_alloc_lastblock()` makes sure the last partial block exists and zeroes tail fragments for indirect-region truncation before shrinking.

## Risks
The code supports both 32-bit UFS1 and 64-bit UFS2 block pointers; pointer-size decisions must match superblock type flags. Truncation recursively frees indirect trees and clears metadata pointers, so interrupted or inconsistent accounting could leak or double-free blocks.
