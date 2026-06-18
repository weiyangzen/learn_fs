# File Research: sources/teaching/minix/minix/fs/ext2/inode.c

This file manages the in-core ext2 inode cache and disk inode read/write.

Key entry points:
- `fs_putnode(ino_nr, count)`: VFS putnode hook, decrements inode references.
- `init_inode_cache()`: initializes unused inode queue and hash lists.
- `get_inode(dev, numb)`: looks up or loads an inode, manages hash/LRU state.
- `find_inode(dev, numb)`: returns an active inode without opening a new disk inode.
- `put_inode(rip)`: drops a reference, truncates and frees unlinked inodes, writes dirty inodes, returns blocks from preallocation.
- `update_times(rip)`: applies pending atime/ctime/mtime flags.
- `rw_inode(rip, rw_flag)`: maps inode number to inode-table block and copies disk/in-core inode fields.
- `dup_inode(ip)`: increments reference count.

Data structures:
- Uses `hash_inodes[INODE_HASH_SIZE]` plus `unused_inodes` tail queue.
- Tracks cache hit/miss counters.

Disk conversion:
- `icopy()` translates between `struct inode` and `d_inode`, using `conv2/conv4` for endian conversion and preserving OS-dependent fields.

Notable behavior:
- On final put of an unlinked inode, calls `truncate_inode()` then `free_inode()`.
- Always discards preallocated blocks when an inode becomes unused.
- New cache entries initialize preallocation fields from `opt.use_prealloc`.
