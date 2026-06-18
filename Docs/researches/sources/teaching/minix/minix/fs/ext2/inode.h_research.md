# File Research: sources/teaching/minix/minix/fs/ext2/inode.h

This header defines the ext2 in-core inode table.

Structure:
- First section mirrors ext2 disk inode fields: mode, UID/GID, size, timestamps, link count, block count, flags, OS-dependent fields, block pointers, ACL fields.
- Second section adds in-memory state: device, inode number, reference count, superblock pointer, dirty flag, block allocation search hints, directory search hints, mountpoint flag, seek/update flags, preallocation state, hash and unused-list links.

Globals:
- `inode[NR_INODES]`: in-core inode table.
- `unused_inodes`: tail queue of free/unused inode slots.
- `hash_inodes`: inode hash table.
- `inode_cache_hit`, `inode_cache_miss`.

Important fields:
- `i_bsearch` and `i_last_pos_bl_alloc` support locality and preallocation.
- `i_last_dpos` and `i_last_dentry_size` accelerate directory insertion.
- `i_prealloc_blocks`, `i_prealloc_count`, `i_prealloc_index`, `i_preallocation` support sequential-write preallocation.
