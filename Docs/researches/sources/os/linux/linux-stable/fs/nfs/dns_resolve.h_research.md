# File Research: sources/os/linux/linux-stable/fs/nfs/dns_resolve.h

## Role

`dns_resolve.h` declares the NFS DNS resolver interface and the maximum supported hostname length for the userspace-cache parser.

## Contents

- `NFS_DNS_HOSTNAME_MAXLEN` is `128`.
- When `CONFIG_NFS_USE_KERNEL_DNS` is enabled, resolver global/per-net init and destroy functions are static inline no-ops because `dns_resolve.c` directly uses the kernel DNS resolver.
- Otherwise it declares `nfs_dns_resolver_init()`, `nfs_dns_resolver_destroy()`, `nfs_dns_resolver_cache_init()`, and `nfs_dns_resolver_cache_destroy()`.
- It always declares `nfs_dns_resolve_name(struct net *net, char *name, size_t namelen, struct sockaddr_storage *sa, size_t salen)`.

## Integration

The header lets common NFS initialization and net namespace code call resolver setup without caring which DNS backend was compiled. It also exposes the actual resolution function used by NFSv4 namespace/referral handling.
