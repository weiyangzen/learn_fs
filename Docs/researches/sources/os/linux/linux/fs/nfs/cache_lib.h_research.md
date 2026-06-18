# File Research: sources/os/linux/linux/fs/nfs/cache_lib.h

## Purpose
Declares shared NFS client cache helper structures and APIs implemented in `cache_lib.c`.

## Main Contents
- Defines `struct nfs_cache_defer_req`, wrapping:
  - `struct cache_req req`
  - `struct cache_deferred_req deferred_req`
  - `struct completion completion`
  - `refcount_t count`
- Declares cache upcall and deferred request helpers.
- Declares rpc_pipefs registration helpers for network namespaces and superblocks.

## Exported API
- `nfs_cache_upcall()`
- `nfs_cache_defer_req_alloc()`
- `nfs_cache_defer_req_put()`
- `nfs_cache_wait_for_upcall()`
- `nfs_cache_register_net()`
- `nfs_cache_unregister_net()`
- `nfs_cache_register_sb()`
- `nfs_cache_unregister_sb()`

## Dependencies
Includes Linux completion, SUNRPC cache, and atomic/refcount headers.

## Integration Points
Included by NFS cache implementations needing deferred upcall behavior or pipefs cache registration.
