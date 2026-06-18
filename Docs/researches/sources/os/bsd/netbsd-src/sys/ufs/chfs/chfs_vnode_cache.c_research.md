# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_vnode_cache.c

Purpose: Implements the CHFS vnode-cache hash table used to map inode numbers to `struct chfs_vnode_cache` records.

Key entry points:
- `chfs_vnocache_hash_init`: allocates hash buckets.
- `chfs_vnode_cache_get`: finds a cache record by vnode number.
- `chfs_vnode_cache_add`: inserts a cache record sorted by vnode number within a bucket.
- `chfs_vnode_cache_remove`: removes a cache record and frees it unless it is in reading/clearing state.
- `chfs_vnocache_hash_destroy`: frees all cache records from all buckets.

Important behavior:
- Bucket index is `vno % VNODECACHE_SIZE`.
- Bucket chains are sorted ascending by `vno`.
- Adding a cache with `vno == 0` assigns a fresh vnode number by incrementing `chm_max_vno`.
- All get/add/remove operations assert `chm_lock_vnocache` ownership.

Dependencies:
- Allocation/freeing is supplied by `chfs_malloc.c`.
- Used by scan, mount/vget, vnode ops, GC, and read-inode state management.

Research notes:
- `chfs_vnocache_hash_destroy` frees bucket contents but does not free the hash array allocation in this file.
