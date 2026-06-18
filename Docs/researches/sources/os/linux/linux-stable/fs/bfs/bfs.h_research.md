# File Research: sources/os/linux/linux-stable/fs/bfs/bfs.h

This is the private BFS header for in-core structures and cross-file declarations.

Key definitions:
- Includes public on-disk definitions from `<linux/bfs_fs.h>`.
- `BFS_MAX_LASTI` is 513, with a detailed comment explaining the practical root-directory limit that prevents filling all theoretical 512 inodes.
- `struct bfs_sb_info` tracks total/free blocks, free inodes, last file end block, last inode number, inode bitmap, and a global `bfs_lock`.
- `struct bfs_inode_info` stores disk inode number, start/end blocks, metadata buffer tracking, and embedded VFS inode.

Helpers:
- `BFS_SB()` gets private superblock state.
- `BFS_I()` converts a VFS inode to BFS private inode state.
- `printf` macro prefixes BFS error logging.

Exports:
- `bfs_iget()`, `bfs_dump_imap()`
- file inode/file/address-space operations
- directory inode/file operations

Integration:
- Included by all BFS implementation files.
- Uses `mapping_metadata_bhs` for metadata fsync support.

Risk notes:
- BFS serialization is coarse-grained through one superblock mutex.
