# File Research: sources/os/linux/linux/fs/nfs/dns_resolve.c

## Role

`dns_resolve.c` resolves NFS hostnames to socket addresses. It has two build-time modes: direct kernel DNS resolver use under `CONFIG_NFS_USE_KERNEL_DNS`, or a SUNRPC cache/upcall resolver path when kernel DNS is not used.

The exported resolver function is `nfs_dns_resolve_name()`.

## Kernel DNS Mode

When `CONFIG_NFS_USE_KERNEL_DNS` is enabled, `nfs_dns_resolve_name()` calls `dns_query()` and converts the returned textual IP address into a `sockaddr` with `rpc_pton()`. Failed DNS lookup maps to `-ESRCH`. The temporary address string is freed after conversion.

## Upcall Cache Mode

Without kernel DNS, the file defines `struct nfs_dns_ent`, a SUNRPC cache entry containing hostname, address, address length, cache header, and RCU free state. Entries are hashed by hostname using a 4-bit hash table.

The cache implementation provides:
- `nfs_dns_ent_alloc()`, `nfs_dns_ent_init()`, `nfs_dns_ent_update()`, and `nfs_dns_ent_put()` for allocation, copy/update, and RCU freeing.
- `nfs_dns_match()` and `nfs_dns_hash()` for cache identity.
- `nfs_dns_request()` and `nfs_dns_upcall()` for userspace resolver upcalls through rpc_pipefs/cache infrastructure.
- `nfs_dns_parse()` for userspace replies containing IP address, hostname, and TTL.
- `nfs_dns_show()` for seq_file cache display.

`nfs_dns_resolve_name()` builds a key from the requested hostname, obtains the network namespace’s `nfs_dns_resolve` cache from `struct nfs_net`, waits for upcall completion through `do_cache_lookup_wait()`, copies the resolved address to caller storage, maps negative cache entries to `-ESRCH`, and returns address length or an error.

## Namespace And Pipefs Lifecycle

`nfs_dns_resolver_cache_init()` creates a per-net cache from `nfs_dns_resolve_template` and registers it with NFS cache infrastructure. `nfs_dns_resolver_cache_destroy()` unregisters and destroys it.

`nfs_dns_resolver_init()` registers per-net operations and an rpc_pipefs notifier. The notifier registers/unregisters the cache for each rpc_pipefs mount/umount event. `nfs_dns_resolver_destroy()` reverses those registrations.

## Error Handling

The upcall path distinguishes missing cache allocation (`-ENOMEM`), pending/expired entries (`-ETIMEDOUT` or `-EAGAIN` internally), negative DNS entries (`-ENOENT` mapped to `-ESRCH`), and caller buffer too small (`-EOVERFLOW`).
