# File Research: sources/os/linux/linux/fs/nilfs2/ifile.c

This file implements NILFS2’s inode file, a metadata file that stores on-disk inode entries and uses the persistent allocator framework.

Data model:
- `struct nilfs_ifile_info` extends metadata-file state with a palloc cache.
- Inode entries are addressed by inode number through palloc block groups.
- Mapping/unmapping of raw inode entries is defined inline in `ifile.h`.

Inode allocation:
- `nilfs_ifile_create_inode()` allocates a new palloc entry starting at `NILFS_FIRST_INO`, gets/creates the entry block, commits allocator state, marks the entry block and ifile dirty, and returns the inode number plus held buffer head.

Inode deletion:
- `nilfs_ifile_delete_inode()` prepares freeing the palloc entry, gets the entry block, clears raw inode flags, marks the buffer dirty, releases it, and commits allocator free state.

Lookup and stats:
- `nilfs_ifile_get_inode_block()` validates inode number with `NILFS_VALID_INODE()`, gets the corresponding palloc entry block, and logs read errors.
- `nilfs_ifile_count_free_inodes()` combines root inode count with palloc max-entry calculation to estimate free inodes.

Initialization:
- `nilfs_ifile_read()` gets or creates `NILFS_IFILE_INO` for a root/checkpoint.
- On a new inode, it initializes metadata-file state, initializes palloc block groups using inode size, sets up palloc cache, and reads checkpoint data through `nilfs_cpfile_read_checkpoint()`.

Important invariants:
- The ifile belongs to a `nilfs_root`; checkpoint reading populates both root counts and ifile raw inode state.
- Allocation returns a live buffer head containing the newly allocated raw inode entry for later inode initialization.
- Deleted raw inode flags are cleared before allocator free commit.
