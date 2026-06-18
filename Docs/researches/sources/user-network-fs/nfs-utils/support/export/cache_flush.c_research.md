# sources/user-network-fs/nfs-utils/support/export/cache_flush.c

## Purpose
Flushes knfsd and sunrpc authentication/export caches after export state changes. It prefers generic netlink cache-flush commands and falls back to the historical `/proc/net/rpc/*/flush` files.

## Important APIs, Types, and Functions
`cache_flush()` is the public entry point. Helpers include `nl_send_flush()`, `cache_nl_flush()`, and `cache_proc_flush()`. It uses `NFSD_CMD_CACHE_FLUSH`, `SUNRPC_CMD_CACHE_FLUSH`, `NFSD_FAMILY_NAME`, and `SUNRPC_FAMILY_NAME`.

## Control Flow
`cache_flush()` tries netlink unless global `no_netlink` is set. `cache_nl_flush()` opens a genetlink socket, enables `NETLINK_EXT_ACK`, resolves and flushes the sunrpc family first, then flushes nfsd if available. On failure it writes a future timestamp to procfs flush files in dependency order.

## State and Persistence Behavior
No repository state is persisted. Effects are kernel cache invalidations through netlink or procfs. The only process state consulted is `no_netlink`; procfs writes use current time plus one second for old kernels.

## Dependencies and Integration Points
Depends on libnl generic netlink, generated or system nfsd/sunrpc netlink UAPI headers, `nfslib.h`, `xlog.h`, and `compat.h`. It integrates with exportfs/mountd paths that need kernel cache invalidation after export table updates.

## Risks and Edge Cases
Ordering is significant because filehandle cache entries reference export cache entries. Netlink family absence triggers fallback or partial success. Procfs paths may be missing when nfsd is not running; write failures are warning-only. Timestamp semantics differ across kernel versions.

## Test Signals
Exercise netlink success, missing sunrpc/nfsd families, `no_netlink` fallback, absent procfs cache files, and short write/error handling. Integration signals are export changes becoming visible to knfsd without stale auth/export results.
