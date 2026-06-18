# File Research: sources/os/linux/linux-stable/fs/nilfs2/ifile.c

## Summary
Implements the NILFS inode file, a metadata file backed by the persistent allocator that stores on-disk inode records.

## Main Responsibilities
- Allocates new inode numbers and inode record blocks.
- Frees inode records.
- Retrieves the block containing a specific inode.
- Counts free inode capacity.
- Reads and initializes an ifile for a checkpoint root.

## Important Behavior
`nilfs_ifile_create_inode()` starts allocation at `NILFS_FIRST_INO`, prepares allocator state, obtains the entry block with create mode, commits the allocation, marks the entry block and metadata file dirty, and returns both inode number and held buffer.

`nilfs_ifile_delete_inode()` prepares freeing, reads the entry block, clears raw inode flags, marks the block dirty, releases it, and commits allocator free state.

`nilfs_ifile_get_inode_block()` validates inode numbers with `NILFS_VALID_INODE()` before reading the allocator entry block. `nilfs_ifile_count_free_inodes()` uses the mounted root's inode count and palloc maximum entry count.

`nilfs_ifile_read()` initializes metadata/palloc state and then loads ifile contents from the checkpoint file into the supplied root.

## Risks
Create returns a buffer reference that later inode code owns. Deletion clears only raw inode flags before freeing allocator state. If checkpoint loading fails, the new inode is failed through `iget_failed()`.
