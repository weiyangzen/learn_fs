# File Research: sources/os/linux/linux/fs/nfs/dns_resolve.h

## Role

`dns_resolve.h` declares the NFS DNS resolver interface and the maximum hostname length used by the userspace-upcall parser.

`NFS_DNS_HOSTNAME_MAXLEN` is `128`.

## Interfaces

The header declares `nfs_dns_resolve_name()` for resolving a hostname in a network namespace into a `sockaddr_storage`.

When `CONFIG_NFS_USE_KERNEL_DNS` is enabled, resolver cache lifecycle functions are inline no-ops because `dns_resolve.c` uses `dns_query()` directly. Otherwise, it declares:
- `nfs_dns_resolver_init()`
- `nfs_dns_resolver_destroy()`
- `nfs_dns_resolver_cache_init(struct net *net)`
- `nfs_dns_resolver_cache_destroy(struct net *net)`

## Integration

This header is included by NFS resolver setup code and by `dns_resolve.c`. It hides the implementation difference between kernel DNS and rpc_pipefs cache/upcall DNS.
