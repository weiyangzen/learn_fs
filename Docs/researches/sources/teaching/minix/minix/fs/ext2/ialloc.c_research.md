# File Research: sources/teaching/minix/minix/fs/ext2/ialloc.c

This file implements ext2 inode allocation and deallocation.

Key entry points:
- `alloc_inode(parent, bits, uid, gid)`: allocates an inode bitmap bit, obtains an in-core inode slot, initializes ownership/mode/device/superblock fields, and wipes block-related fields.
- `free_inode(rip)`: frees the inode bitmap bit and marks the in-core inode not allocated.

Allocation strategies:
- `find_group_any()`: MFS-like first group with free inode, starting at `s_igsearch`.
- `find_group_hashalloc()`: BSD-like placement for non-directories, trying parent group, quadratic probing, then linear fallback.
- `find_group_dir()`: Linux-like directory placement by average free inode count and best free block count.
- `find_group_orlov()`: Orlov allocator for spreading top-level directories and placing child entries in sufficiently free groups.

Metadata updates:
- Updates group and superblock free inode counts.
- Updates used directory counts for directory inodes.
- Sets `group_descriptors_dirty`.
- Maintains `s_igsearch` on inode free.

Notable safeguards:
- Rejects/reserves inodes below `EXT2_FIRST_INO(sp)`.
- Panics if allocator returns an inode beyond `s_inodes_count`.
- Panics on freeing invalid or already-free inode bits.
