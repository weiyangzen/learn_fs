# File Research: sources/os/linux/linux-stable/fs/nfs/pnfs_dev.c

This file implements the global pNFS device-id cache. A device ID is unique per layout driver and NFS client, and maps to layout-driver-specific device information obtained through NFSv4.1 GETDEVICEINFO.

Cache structure:
- The cache is a fixed 32-bucket hash table: `nfs4_deviceid_cache`.
- `nfs4_deviceid_lock` protects hash insertion/removal and purge operations.
- Readers use RCU over hash buckets.
- Nodes are `struct nfs4_deviceid_node`, declared in `pnfs.h`, with layout-driver pointer, NFS client pointer, flags, unavailable timestamp, deviceid, RCU node, temporary purge node, and atomic refcount.

Important functions:
- `nfs4_deviceid_hash()` hashes the raw 16-byte NFSv4 deviceid using a simple multiply-by-37 byte fold.
- `_lookup_deviceid()` searches one hash bucket for matching layout driver, client, and deviceid, ignoring nodes whose refcount is zero.
- `nfs4_get_device_info()` allocates a `pnfs_device`, page array, and reply pages, sizes GETDEVICEINFO from the session max response size, calls `nfs4_proc_getdeviceinfo()`, then asks the active layout driver to decode and allocate a device-id node. It marks `NFS_DEVICEID_NOCACHE` if the server says the device may not be cached.
- `nfs4_find_get_deviceid()` first looks up an existing cache node and takes a reference; on a miss it fetches device info, then races safely against another inserter under the device-id lock.
- `nfs4_delete_deviceid()` unhashes a node, clears no-cache state, and drops the initial cache reference.
- `nfs4_init_deviceid_node()` initializes layout-driver-owned nodes before insertion.
- `nfs4_put_deviceid_node()` decrements references and frees through `ld->free_deviceid_node()` at zero. No-cache nodes trigger deletion when their active reference count reaches the special threshold.
- `nfs4_mark_deviceid_available()`, `nfs4_mark_deviceid_unavailable()`, and `nfs4_test_deviceid_unavailable()` implement temporary device backoff with `PNFS_DEVICE_RETRY_TIMEOUT`.
- `nfs4_deviceid_purge_client()` removes all cached device IDs for a client when pNFS MDS use is active.
- `nfs4_deviceid_mark_client_invalid()` marks all client device IDs invalid, typically after lease/state recovery requires clients to stop using old device mappings.

Concurrency and lifetime:
- RCU permits lockless cache lookup while deletion uses `hlist_del_init_rcu()`.
- The hash lock serializes insertion, deletion, and purge list construction.
- Atomic references protect nodes while in use by layout drivers or I/O paths.
- Purge first unhashes matching nodes into a temporary hlist, then drops references outside the spinlock.

Error and retry behavior:
- GETDEVICEINFO allocation or RPC failure returns no node and traces `nfs4_find_deviceid(..., -ENOENT)`.
- Unavailable device IDs remain suppressed until their timestamp ages out of `PNFS_DEVICE_RETRY_TIMEOUT`, after which the unavailable flag is cleared and callers may retry.
- Invalid device IDs remain flagged for layout-driver logic to reject or refresh mappings.

Role in the pNFS stack:
- `pnfs.c` manages layouts and layout segments; this file manages the device IDs referenced by layout-driver-private segments.
- `pnfs_nfs.c` uses data-server objects and connections, while this file handles the lower-level device-id cache and GETDEVICEINFO bridge.
