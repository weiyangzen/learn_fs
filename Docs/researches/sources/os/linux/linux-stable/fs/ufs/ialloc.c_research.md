# File Research: sources/os/linux/linux-stable/fs/ufs/ialloc.c

## Summary
Implements UFS inode allocation and freeing, including cylinder-group inode bitmaps, summary counters, and UFS2 inode chunk initialization.

## Main Responsibilities
- Frees inodes after VFS eviction by clearing inode bitmap bits and updating free inode/directory counters.
- Allocates new inodes near the parent cylinder group, using quadratic rehash then linear fallback.
- Updates cylinder group, global summary, and per-cylinder summary counters.
- Initializes UFS2 inode chunks on demand before allocating from newly initialized inode blocks.
- Initializes VFS inode owner, timestamps, flags, direct block pointers, and lookup cache state.
- Writes UFS2 birth time directly to the on-disk inode.

## Important Behavior
`ufs_free_inode()` is intended to run after `clear_inode()` to avoid aliasing a live inode with a newly reused inode number.

`ufs_new_inode()` inserts the inode locked before returning and marks it dirty after initializing in-core state.

## Risks
Allocator state is protected by `s_lock`; bitmap and summary counter divergence can corrupt future allocations. Error handling has distinct paths for inserted vs non-inserted inode cleanup.
