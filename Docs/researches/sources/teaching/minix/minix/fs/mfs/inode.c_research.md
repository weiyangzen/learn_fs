# File Research: sources/teaching/minix/minix/fs/mfs/inode.c

`inode.c` manages the fixed in-core inode table, including lookup, caching, reference counts, allocation, freeing, timestamp updates, and disk inode serialization. It uses a hash table keyed by inode number masked with `INODE_HASH_MASK` plus an unused/LRU tail queue.

`init_inode_cache` initializes hit/miss counters, all hash buckets, and the unused list. `get_inode` searches the hash, revives cached zero-reference inodes from the unused list, or reuses the first unused slot, loading from disk with `rw_inode` unless `NO_DEV` is used during fresh allocation. `find_inode` is a non-acquiring cache lookup for already-open inodes. `fs_putnode`, `put_inode`, and `dup_inode` implement VFS reference release and local reference duplication.

When the last reference drops, `put_inode` writes dirty inodes, truncates and frees unlinked inodes (`i_nlinks == NO_LINK`), and either evicts freed entries or keeps still-linked entries on the unused list as cacheable inodes. `alloc_inode` allocates an inode bitmap bit, sets owner/mode/superblock fields, and calls `wipe_inode` to reset size, update flags, and zones. `free_inode` clears the inode bitmap bit and updates `s_isearch`.

`rw_inode` locates the disk inode block after boot, superblock, inode map, and zone map blocks, then copies fields through `new_icopy`. Only V3 is accepted; `conv2`/`conv4` handle native/swapped values. `update_times` lazily fills atime/ctime/mtime using `clock_time` unless the filesystem is read-only.
