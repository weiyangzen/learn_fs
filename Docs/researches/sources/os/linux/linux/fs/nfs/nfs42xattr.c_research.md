# File Research: sources/os/linux/linux/fs/nfs/nfs42xattr.c

This file implements the client-side cache for NFSv4.2 user extended attributes. The cache is attached lazily to NFS inodes and stores both individual name/value xattrs and a special cached `listxattr` result.

Key structures:
- `struct nfs4_xattr_cache`: per-inode cache with 64 buckets, LRU/dispose nodes, entry count, listxattr lock, inode pointer, and special listxattr entry pointer.
- `struct nfs4_xattr_bucket`: spinlock-protected hash bucket with a `draining` flag and back-pointer to the cache.
- `struct nfs4_xattr_entry`: refcounted xattr or listxattr entry with hash node, LRU node, dispose node, name, value, size, bucket, and allocation flags.
- Global LRUs: one for cache objects, one for normal entries, and one for large entries whose values are separately allocated with `kvmalloc()`.

Main behavior:
- `nfs4_xattr_alloc_entry()` co-allocates the entry, name, and small value in one `kmalloc()` allocation, but uses an external `kvmalloc()` value for entries too large for one page.
- `nfs4_xattr_get_cache()` obtains or lazily creates a referenced inode cache. It unlinks stale caches when `NFS_INO_INVALID_XATTR` is set and avoids allocation while holding `inode->i_lock`.
- `nfs4_xattr_cache_get()` retrieves a named xattr, supporting length probes and `-ERANGE` for short caller buffers.
- `nfs4_xattr_cache_list()` retrieves the cached listxattr payload with the same length-probe behavior.
- `nfs4_xattr_cache_add()` replaces or inserts a named xattr and invalidates cached listxattr output.
- `nfs4_xattr_cache_remove()` removes a named xattr and invalidates cached listxattr output.
- `nfs4_xattr_cache_set_list()` stores listxattr output as a special entry not tied to a hash name.
- `nfs4_xattr_cache_zap()` unlinks the whole cache from an evicted or invalidated inode and discards its entries.

Shrinker design:
- The cache shrinker removes mostly empty cache structures after unlinking them from inodes.
- The normal entry shrinker reclaims ordinary cache entries.
- The large entry shrinker reclaims large entries more aggressively with `seeks = 1`.
- Shrinker isolation uses `trylock` because it can invert normal lock ordering; skipped objects are acceptable.

Locking and lifetime:
- Documented lock order is inode `i_lock` or bucket lock before the `list_lru` lock.
- Cache and entry lifetimes use `kref`.
- `ERR_PTR(-ESTALE)` in `cache->listxattr` marks a draining list cache so stale references cannot repopulate it.
- Cache unlinking requires `inode->i_lock`; bucket mutation requires the relevant bucket lock.
- Entry LRU membership and hash/list membership must be removed before the last `kref_put()`.

Risk areas:
- Refcount and LRU membership are tightly coupled; free callbacks warn if an entry remains on an LRU.
- Draining flags are the defense against racing writers repopulating stale caches.
- Large xattr memory pressure behavior depends on correct selection of `NFS4_XATTR_ENTRY_EXTVAL`.
- Shrinker callbacks deliberately skip locked objects; changing lock ordering here risks deadlock.
