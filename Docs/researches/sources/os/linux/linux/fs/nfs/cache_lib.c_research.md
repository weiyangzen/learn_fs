# File Research: sources/os/linux/linux/fs/nfs/cache_lib.c

## Purpose
Provides shared helper routines for NFS client cache upcalls and cache pipefs registration. It supports synchronous userspace cache lookup helpers and deferred cache request completion.

## Main Responsibilities
- Invoke `/sbin/nfs_cache_getent` or a configured helper for cache misses.
- Disable broken helper execution after `ENOENT` or `EACCES`.
- Allocate, reference, complete, and free deferred cache requests.
- Register and unregister NFS cache details with rpc_pipefs per superblock or per network namespace.

## Key Functions
- `nfs_cache_upcall()` calls the configured helper with cache name and entry name.
- `nfs_cache_defer_req_alloc()` allocates and initializes a deferred cache request with completion and refcount.
- `nfs_cache_wait_for_upcall()` waits for completion up to `cache_getent_timeout`.
- `nfs_cache_register_sb()` registers a `cache_detail` under the `cache` rpc_pipefs directory.
- `nfs_cache_register_net()` initializes cache detail and registers it if rpc_pipefs is mounted.
- `nfs_cache_unregister_net()` unregisters pipefs state and destroys cache detail.

## Control Flow
A cache miss can allocate `nfs_cache_defer_req`, install its defer callback, trigger a userspace upcall, and wait for `nfs_dns_cache_revisit()` to complete the request. Pipefs registration uses `rpc_get_sb_net()` to register only when an rpc_pipefs superblock exists for the net namespace.

## Data and Ownership
- `nfs_cache_defer_req` is refcounted.
- Deferred request revisit completes the waiter and drops the defer reference.
- `sunrpc_init_cache_detail()` and `sunrpc_destroy_cache_detail()` bracket cache-detail lifetime.

## Configuration
- `cache_getent` module parameter controls helper path.
- `cache_getent_timeout` controls wait duration in seconds.
- Default helper path is `/sbin/nfs_cache_getent`.
- Default timeout is 15 seconds.

## Risks and Edge Cases
- Helper path is disabled in memory after `ENOENT` or `EACCES`, requiring admin reset through module parameters.
- `nfs_cache_register_net()` returns success if rpc_pipefs is not mounted, so consumers must tolerate delayed registration.
- Waiting callers see `-ETIMEDOUT` if completion does not arrive before the configured timeout.

## Integration Points
Used by NFS client cache implementations that rely on SUNRPC cache infrastructure and rpc_pipefs exposure.
