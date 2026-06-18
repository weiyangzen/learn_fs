# File Research: sources/os/linux/linux/fs/nfs/pnfs_dev.c

## Purpose
`pnfs_dev.c` implements the pNFS deviceid cache. Deviceids identify pNFS data devices for a given layout driver and NFS client. This file looks up cached deviceids, fetches missing device information with `GETDEVICEINFO`, inserts deviceid nodes with RCU protection, handles no-cache/unavailable state, deletes entries, purges client entries, and marks client deviceids invalid.

## Cache Structure
- Uses a global 32-bucket hash table: `NFS4_DEVICE_ID_HASH_BITS` is 5.
- Cache is protected by `nfs4_deviceid_lock` plus RCU list traversal.
- A cache key is `(layout driver, nfs_client, nfs4_deviceid)`.
- Hashing walks raw deviceid bytes with a simple multiply-by-37 accumulator.

## Lookup and Population
- `_lookup_deviceid()` scans one hash bucket and returns a matching node with nonzero refcount.
- `__nfs4_find_get_deviceid()` performs RCU lookup and takes a reference with `atomic_inc_not_zero()`.
- `nfs4_find_get_deviceid()` first checks cache, then calls `nfs4_get_device_info()` on miss, then rechecks under lock to handle races before inserting a new node.
- If another thread inserted the same deviceid during fetch, the newly decoded node is freed through the layout driver.

## GETDEVICEINFO Flow
- `nfs4_get_device_info()` sizes the reply buffer from the session max response size.
- Allocates a `struct pnfs_device`, a page pointer array, and reply pages.
- Fills layout type, deviceid, page buffer fields, and maxcount adjusted by `nfs41_maxgetdevinfo_overhead`.
- Calls `nfs4_proc_getdeviceinfo()`.
- Delegates decoded deviceid-node allocation to `pnfs_curr_ld->alloc_deviceid_node()`.
- Preserves `pdev->nocache` as `NFS_DEVICEID_NOCACHE` on the node.
- Frees temporary pages and `pnfs_device` storage regardless of success.

## Deletion and Refcounting
- `nfs4_init_deviceid_node()` initializes hash nodes, layout-driver/client key fields, flags, deviceid, and refcount.
- `nfs4_delete_deviceid()` removes a matching cache node under the cache lock, clears nocache, and drops the initial cache reference.
- `nfs4_put_deviceid_node()` handles normal refcount drop. For no-cache entries, it forces deletion when only cache/user refs remain, then frees through the layout driver when refcount reaches zero.
- Deviceid frees are traced through `trace_nfs4_deviceid_free()`.

## Availability and Invalidation
- `nfs4_mark_deviceid_unavailable()` stores `jiffies` and sets `NFS_DEVICEID_UNAVAILABLE`.
- `nfs4_test_deviceid_unavailable()` suppresses reuse during `PNFS_DEVICE_RETRY_TIMEOUT`; after the timeout, it clears the unavailable bit.
- `nfs4_mark_deviceid_available()` clears temporary unavailable state.
- `nfs4_deviceid_mark_client_invalid()` marks every cached deviceid for a client with `NFS_DEVICEID_INVALID`.
- `nfs4_deviceid_purge_client()` removes and puts all cached deviceids for a client when pNFS MDS exchange flags indicate pNFS use.

## Integration Points
- Depends on layout-driver callbacks `alloc_deviceid_node()` and `free_deviceid_node()`.
- Called by layout drivers that need to map layout deviceids to concrete data-server/device state.
- Includes `nfs4trace.h` and emits find/free tracepoints.
- Works with `pnfs.h` deviceid flags and with NFSv4 session sizing from `nfs4session.h`.

## Invariants and Risks
- RCU lookup plus atomic refcounting protects readers from nodes being freed while found.
- The second cache lookup after `GETDEVICEINFO` is required to avoid duplicate insertion.
- Nocache handling is subtle because the node can still be briefly hashed and referenced.
- Temporary unavailability is time-window based; callers must call `nfs4_test_deviceid_unavailable()` before reconnect attempts.
- Client purge first unhashes into a temporary list, then drops refs outside the global lock to avoid freeing under the cache lock.
