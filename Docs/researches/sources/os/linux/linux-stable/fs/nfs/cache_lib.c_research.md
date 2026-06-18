# File Research: sources/os/linux/linux-stable/fs/nfs/cache_lib.c

## Purpose

`cache_lib.c` provides helper routines for NFS client caches that use SUNRPC cache infrastructure and rpc_pipefs. It supports userspace cache upcalls, deferred request waiting, and per-net/per-superblock cache registration.

## Main Responsibilities

- Invoke the configurable `/sbin/nfs_cache_getent` helper to populate cache entries.
- Disable the helper path automatically after `ENOENT` or `EACCES` failures.
- Allocate, reference, complete, and free deferred cache requests.
- Wait for deferred cache upcalls with a configurable timeout.
- Register and unregister `cache_detail` instances under rpc_pipefs `cache/`.

## Key Functions

- `nfs_cache_upcall()` builds helper argv as `<helper> <cache-name> <entry-name>`, uses `call_usermodehelper(..., UMH_WAIT_EXEC)`, and maps positive helper returns to success.
- `nfs_cache_defer_req_alloc()` creates `struct nfs_cache_defer_req`, initializes completion and refcount, and installs the `defer` callback.
- `nfs_dns_cache_defer()` increments the deferred request refcount and returns the embedded `cache_deferred_req`.
- `nfs_dns_cache_revisit()` completes the waiting request and drops the deferred reference.
- `nfs_cache_wait_for_upcall()` waits up to `cache_getent_timeout` seconds.
- `nfs_cache_register_net()` initializes a cache detail and registers it against a mounted rpc_pipefs superblock if one exists.
- `nfs_cache_unregister_net()` unregisters from pipefs if mounted and always destroys the cache detail.

## Control Flow and State

Two module parameters control userspace behavior: `cache_getent` and `cache_getent_timeout`. Deferred requests use a completion plus refcount so a waiting kernel caller and SUNRPC cache revisit path can coordinate lifetime. The registration helpers tolerate rpc_pipefs not being mounted by initializing/destroying cache details independently from pipefs visibility.

## Integration Points

- Uses `<linux/sunrpc/cache.h>` for `cache_detail`, `cache_req`, and deferred request callbacks.
- Uses rpc_pipefs lookup and registration helpers.
- Provides shared helpers for NFS client caches such as DNS or id-mapping style caches.

## Risks and Edge Cases

- The helper path is globally disabled after missing/inaccessible executable errors until the module parameter is changed.
- Waiting is bounded by the module timeout, but the caller must still release deferred request references correctly.
- `nfs_cache_register_sb()` assumes the `cache` dentry lookup result is suitable for `sunrpc_cache_register_pipefs()` and always `dput()`s it.

## Testing Focus

Test helper success/failure path disabling, timeout behavior, revisit completion, refcount release ordering, register/unregister with and without mounted rpc_pipefs, and cache detail cleanup after registration failure.
