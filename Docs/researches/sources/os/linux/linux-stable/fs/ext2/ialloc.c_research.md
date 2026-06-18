# File Research: sources/os/linux/linux-stable/fs/ext2/ialloc.c

## Summary
Implements ext2 inode allocation and freeing, including group-selection policy, inode bitmap updates, group descriptor accounting, quota setup, ACL/security initialization, and free inode/directory counting.

## Main Responsibilities
- Reads inode bitmaps.
- Frees inode bitmap bits and updates free inode/directory counters.
- Selects block groups for new directory and non-directory inodes.
- Implements the Orlov directory allocator and older directory allocation mode.
- Allocates inodes, initializes ext2 private inode fields, inserts locked inodes, and initializes quota/ACL/security state.
- Counts free inodes and directories.

## Key APIs
- `ext2_new_inode()`.
- `ext2_free_inode()`.
- `ext2_count_free_inodes()`.
- `ext2_count_dirs()`.

## Important Behavior
Directory placement uses either old allocation or Orlov allocation. Orlov spreads top-level directories, uses average free inode/block counts, directory counts, and per-group debt to avoid clustering too many directories in one group. Non-directories prefer the parent group, then use quadratic probing, then linear fallback.

`ext2_new_inode()` sets the inode bitmap bit atomically, updates group descriptors and percpu counters, initializes ownership, ext2 flags inherited from the parent, generation number, ACLs, security xattrs, quotas, and async prereads the target inode table block.

`ext2_free_inode()` drops quota state first, validates inode number, clears the bitmap bit atomically, adjusts directory counts if needed, and syncs the bitmap on synchronous mounts.

## State and Synchronization
Bitmap updates use per-blockgroup locks. Group descriptor free inode and used directory counters are updated under the same lock. The generation counter is protected by `s_next_gen_lock`.

## Risks
Allocator decisions use approximate percpu counters, so allocation must handle races where a selected group has no free inodes by continuing the scan. Failure after bitmap allocation must go through `discard_new_inode()` and quota cleanup paths to avoid leaks.
