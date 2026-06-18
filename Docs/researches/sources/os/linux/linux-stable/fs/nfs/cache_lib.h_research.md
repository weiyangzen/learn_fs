# File Research: sources/os/linux/linux-stable/fs/nfs/cache_lib.h

## Purpose

`cache_lib.h` declares the shared NFS client cache helper API and the deferred request container used by `cache_lib.c`.

## Main Contents

- Defines `struct nfs_cache_defer_req`, embedding:
  - `struct cache_req req`
  - `struct cache_deferred_req deferred_req`
  - `struct completion completion`
  - `refcount_t count`
- Declares userspace upcall, deferred request allocation/free/wait, and cache registration helpers.

## Integration Points

Consumers include NFS cache implementations that need to defer lookups while a userspace helper populates SUNRPC cache entries. The header depends on Linux completion, SUNRPC cache, and atomic/refcount definitions.

## API Notes

The caller owns the initial `nfs_cache_defer_req` reference returned by `nfs_cache_defer_req_alloc()` and must release it with `nfs_cache_defer_req_put()`. The deferred path takes its own reference before returning a `cache_deferred_req` to SUNRPC cache code.

## Testing Focus

Header-level review should verify all users pair allocation with `nfs_cache_defer_req_put()`, wait only on initialized requests, and unregister cache details in the same namespace/superblock context where they were registered.
