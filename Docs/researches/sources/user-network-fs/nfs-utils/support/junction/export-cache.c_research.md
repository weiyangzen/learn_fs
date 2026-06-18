# sources/user-network-fs/nfs-utils/support/junction/export-cache.c

## Purpose
Flushes kernel NFSD export-related caches for junction updates using procfs cache flush files.

## Important APIs, Types, and Functions
`junction_flush_exports_cache()` and helper `junction_write_time()`.

## Control Flow
The flush function formats current time and writes it to auth.unix.ip, auth.unix.gid, nfsd.fh, and nfsd.export flush files in dependency order. It stops and returns a FedFS status on the first failed open/write.

## State and Persistence Behavior
No internal state. Effects are kernel cache invalidation attempts through `/proc/net/rpc` files.

## Dependencies and Integration Points
Depends on procfs rpc cache files, `junction.h` statuses, and `xlog`. Complements the broader export cache flush code.

## Risks and Edge Cases
Missing proc files return no-cache-update, while write failure returns unknown-cache. Unlike `cache_flush.c`, this path has no netlink mode.

## Test Signals
Test all proc files present, first file missing, later write failure, time failure injection, and ordering.
