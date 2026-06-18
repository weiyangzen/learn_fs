# File Research: sources/os/linux/linux-stable/fs/nfs/nfs42xattr.c

This file implements the client-side cache for NFSv4.2 user extended attributes. The cache is attached lazily to NFS inodes and stores individual xattr name/value pairs plus a special cached `listxattr` result.

Key structures:
- `struct nfs4_xattr_cache`
  - Per-inode cache object.
  - Contains 64 hash buckets, an LRU node, a dispose list node, entry count, listxattr lock, inode pointer, and special `listxattr` entry pointer.
- `struct nfs4_xattr_bucket`
  - Spinlock-protected hash bucket with `draining` flag.
- `struct nfs4_xattr_entry`
  - Refcounted xattr value entry with hash node, LRU node, dispose node, name, value, size, bucket pointer, and flags.
- Global LRUs:
  - `nfs4_xattr_cache_lru` for cache objects.
  - `nfs4_xattr_entry_lru` for normal entries.
  - `nfs4_xattr_large_entry_lru` for entries whose values require separate `kvmalloc()` storage.

Main behavior:
- Entries are allocated by `nfs4_xattr_alloc_entry()`.
  - Small values are co-allocated with the entry/name in one `kmalloc()` allocation.
  - Large values are stored via `kvmalloc()` and placed on the large-entry LRU.
  - Values can be copied either from a direct buffer or from RPC reply pages.
- `nfs4_xattr_get_cache()` obtains or creates a referenced per-inode cache.
  - It handles `NFS_INO_INVALID_XATTR` by unlinking and discarding stale caches.
  - It avoids allocations under `inode->i_lock` via optimistic allocation and race resolution.
- Public cache entry points:
  - `nfs4_xattr_cache_get()` retrieves a named xattr.
  - `nfs4_xattr_cache_list()` retrieves cached list output.
  - `nfs4_xattr_cache_add()` adds/replaces a named entry and invalidates list cache.
  - `nfs4_xattr_cache_remove()` removes a named entry and invalidates list cache.
  - `nfs4_xattr_cache_set_list()` caches `listxattr` output.
  - `nfs4_xattr_cache_zap()` unlinks and discards the entire inode cache.

Shrinker design:
- There are three shrinkers:
  - Cache shrinker: frees cache structures only when they are small/mostly empty.
  - Entry shrinker: reclaims normal entries.
  - Large entry shrinker: reclaims large entries more aggressively with `seeks = 1`.
- Shrinker isolation uses `trylock` paths because it inverts ordinary lock ordering.
- Discarding a cache marks listcache as stale and all buckets as draining before unlinking entries.

Locking and lifetime:
- Documented lock order is inode `i_lock` or bucket lock before list_lru lock.
- Cache and entry lifetimes are protected by `kref`.
- `ERR_PTR(-ESTALE)` in `cache->listxattr` marks a draining list cache and prevents new listcache insertion into stale cache state.
- Cache unlink requires `inode->i_lock`.

Risk areas:
- Refcount and LRU membership must stay synchronized. Free callbacks warn if an entry remains on an LRU.
- Shrinker paths deliberately use `trylock`; missed reclamation is acceptable, but incorrect locking could deadlock.
- The stale-cache/draining flags prevent racing writers from repopulating invalid cache objects.
- Large xattr memory pressure behavior depends on correct `NFS4_XATTR_ENTRY_EXTVAL` flag selection.
