# File Research: sources/os/linux/linux/fs/hpfs/hpfs_fn.h

Purpose: Provides HPFS internal types, constants, inline helpers, prototypes, and locking helpers.

Key content:
- Allocation tuning constants, readahead constants, and error aliases.
- `struct hpfs_inode_info` extends VFS inode with HPFS directory/file caches, EA flags, dirty flag, and active readdir positions.
- `struct hpfs_sb_info` stores global HPFS mount state, options, codepage table, bitmap directory, hotfix map, and global mutex.
- `struct quad_buffer_head` represents four sector buffers plus optional contiguous/bounce data.
- Inline helpers navigate dnodes, dirents, fnodes, EAs, and B+ headers.
- Prototypes for all HPFS source files.
- Time conversion helpers between HPFS local time and Unix GMT.
- `hpfs_lock()`, `hpfs_unlock()`, and `hpfs_lock_assert()` define the filesystem-wide lock discipline.

Dependencies and integration:
- Included by every HPFS implementation file.
- Centralizes cross-file contracts for allocation, mapping, dnode, EA, file, inode, name, and superblock operations.

Risk notes:
- HPFS uses a single global filesystem mutex for VFS methods, simplifying correctness at the cost of concurrency.
- Inline dirent/EA pointer arithmetic assumes validated on-disk bounds.
