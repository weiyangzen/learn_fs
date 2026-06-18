# File Research: sources/os/linux/linux/fs/ext2/ialloc.c

Read status: complete, 673 lines.

This file implements ext2 inode bitmap handling, inode allocation, inode freeing, and directory placement policy.

Key responsibilities:
- Reads inode bitmaps with `read_inode_bitmap()`.
- Frees inodes with `ext2_free_inode()`, including quota release, bitmap clearing, descriptor count updates, and directory counter updates.
- Allocates new inodes with `ext2_new_inode()`.
- Implements classic and Orlov group selection policies for directory placement.
- Implements non-directory group selection that prefers parent locality and falls back to quadratic/linear search.
- Counts free inodes and directory counts from group descriptors.

Allocation policy:
- Directories use either the old allocator or Orlov allocator depending on mount options.
- Orlov allocator spreads top-level directories across groups, considers average free inodes/free blocks, directory counts, and per-group debt.
- Non-directories prefer the parent’s group, then use a hash-like quadratic search, then linear fallback.
- Per-group debt increases for directory allocation and decreases for non-directory allocation.

New inode flow:
- Allocate VFS inode.
- Select target group.
- Read inode bitmap and atomically set a free bit.
- Update free inode counters, directory counters, group descriptor counts, and debts.
- Initialize owner/group according to `GRPID` mount option or normal ownership rules.
- Initialize ext2 inode fields, inherited flags, block group, generation, ACLs, security xattrs, quotas, and dirty state.
- Insert inode locked, preread the inode table block, and return it.

Free inode flow:
- Reject reserved/nonexistent inode numbers.
- Clear the inode bitmap bit atomically.
- Update group descriptor free inode count and used directory count.
- Update percpu free inode and directory counters.
- Sync bitmap buffer for synchronous mounts.

Safety and consistency:
- Bitmap changes use block group locks.
- Inode freeing order avoids inode-number aliasing by relying on VFS inode teardown before bitmap reuse.
- Quota is freed before superblock/group locking to avoid lock recursion.
- Handles races where group selection saw free inodes but bitmap allocation loses to another allocator.

Research notes:
- This file is ext2’s inode counterpart to `balloc.c`.
- The Orlov allocator is the main policy complexity.
