# File Research: sources/os/linux/linux-stable/fs/nfs/dns_resolve.c

## Role

`dns_resolve.c` resolves NFS hostnames into socket addresses. It supports two compile-time implementations: a kernel DNS resolver path when `CONFIG_NFS_USE_KERNEL_DNS` is enabled, and a userspace upcall/cache implementation through SUNRPC cache and rpc_pipefs otherwise. NFSv4 namespace referral code calls `nfs_dns_resolve_name()`.

## Kernel DNS implementation

With `CONFIG_NFS_USE_KERNEL_DNS`, `nfs_dns_resolve_name()` calls `dns_query()` with the network namespace and hostname. A positive DNS response string is converted to a `sockaddr` using `rpc_pton()`. DNS failure maps to `-ESRCH`, and the allocated IP string is freed with `kfree()`. All resolver init/destroy functions are inline no-ops in the header for this configuration.

## SUNRPC cache/upcall implementation

Without kernel DNS, each resolver entry is `struct nfs_dns_ent`: a SUNRPC `cache_head`, hostname and length, resolved `sockaddr_storage`, address length, and RCU head. Entries are hashed by hostname using a 16-bucket hash table.

`nfs_dns_resolve_template` describes the cache: allocation, initialization, update, matching, request formatting, parser, display, upcall, and put/free callbacks. Entry freeing is RCU-delayed and releases the hostname string.

`nfs_dns_upcall()` sets `CACHE_PENDING`, first tries `nfs_cache_upcall()`, and otherwise sends an rpc_pipefs cache upcall with timeout. `nfs_dns_request()` writes the requested hostname into the upcall payload.

Userspace replies are parsed by `nfs_dns_parse()`. The expected line contains an IP address, hostname, and TTL. The parser converts the address with `rpc_pton()`, stores negative entries when address conversion yields zero length, computes expiry from `seconds_since_boot() + ttl`, and updates the cache entry.

## Lookup behavior

`nfs_dns_resolve_name()` builds a temporary key from the requested hostname and uses `do_cache_lookup_wait()`. That function allocates a deferred request, calls `cache_check()`, waits for an upcall on `-EAGAIN`, then does a nowait validation pass. A valid positive entry copies the address into the caller's buffer if it fits; too small a buffer returns `-EOVERFLOW`. Negative cache entries become `-ESRCH`.

Nowait validation rejects entries that are not `CACHE_VALID`, expired, older than cache flush time, or negative. Cache references are put through `cache_put()`.

## Namespace and rpc_pipefs lifecycle

`nfs_dns_resolver_cache_init()` creates a per-net cache from the template and registers it with NFS cache infrastructure; destroy unregisters and destroys it. The file registers pernet operations in `nfs_dns_resolver_init()`.

The rpc_pipefs notifier registers or unregisters the cache against a mounted rpc_pipefs superblock on `RPC_PIPEFS_MOUNT` and `RPC_PIPEFS_UMOUNT`. It takes a module reference around notifier work and ignores namespaces where the cache has not been initialized.

## Error handling

Parsing rejects malformed lines, missing newline, empty qwords, zero TTL, allocation failures, and lookup/update failures. Upcall lookup can return `-ENOMEM`, `-ETIMEDOUT`, `-ENOENT`, `-EAGAIN`, `-EOVERFLOW`, or the mapped public `-ESRCH` for unresolved names.
