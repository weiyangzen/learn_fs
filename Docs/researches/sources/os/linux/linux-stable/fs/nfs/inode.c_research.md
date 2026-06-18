# File Research: sources/os/linux/linux-stable/fs/nfs/inode.c

## Purpose

Provides core NFS inode and superblock support: inode lookup/allocation, attribute caching and revalidation, setattr/getattr, open and lock contexts, page-cache invalidation, weak cache consistency updates, inode slab management, NFS workqueues, per-net setup, and NFS client module initialization.

## Main Entry Points

- `nfs_fhget()` / `nfs_ilookup()`: find or create inodes by filehandle, fileid, and type.
- `nfs_set_cache_invalid()` / `nfs_zap_caches()` / `nfs_clear_invalid_mapping()` / `nfs_revalidate_mapping()`: manage attribute and page-cache invalidation.
- `nfs_getattr()` / `nfs_setattr()` / `nfs_setattr_update_inode()`: VFS attribute operations.
- `__nfs_revalidate_inode()` / `nfs_revalidate_inode()` / `nfs_refresh_inode()` / `nfs_update_inode()`: fetch, compare, and update cached server attributes.
- `nfs_post_op_update_inode()` / `nfs_post_op_update_inode_force_wcc()`: update inode state after mutating operations.
- `alloc_nfs_open_context()` / `nfs_open()` / `nfs_file_set_open_context()` / `nfs_file_clear_open_context()`: file open context lifecycle.
- `nfs_get_lock_context()` / `nfs_put_lock_context()`: per-open lock context lifecycle.
- `nfs_alloc_inode()` / `nfs_free_inode()` and inode cache init/destroy: NFS inode slab lifecycle.
- `init_nfs_fs()` / `exit_nfs_fs()`: global module setup and teardown.

## Control Flow And State

`nfs_fhget()` uses `iget5_locked()` with filehandle-aware matching, initializes new inodes by type, assigns protocol-specific file/dir ops, handles mountpoint/referral automounts, sets initial attributes from fattrs, initializes fscache/netfs state, and refreshes existing inodes. Attribute validity is tracked through `NFS_I(inode)->cache_validity`, with delegations suppressing invalidation of attributes the client owns.

Revalidation flushes pNFS layoutcommit-sensitive state, gets fresh fattrs, refreshes the inode, clears ACL invalidation when needed, and applies security labels. `nfs_update_inode()` compares generation counters and NFSv4 change attributes, handles out-of-order replies, weak cache consistency pre/post data, size changes, writer/delegation races, directory cache invalidation, access/ACL/xattr invalidation, and adaptive attribute timeout growth.

Open contexts hold dentries, credentials, lock context lists, localio state, and close-to-open behavior. Lock contexts are keyed by the caller’s file table. Mapping invalidation serializes `NFS_INO_INVALIDATING` with wait-bit logic so one invalidator clears data while others observe consistent state.

Module initialization sets up keyring support, sysfs, per-net data, workqueues, proc entries, NFS page/read/write/direct caches, inode cache, and filesystem registration; teardown reverses those pieces.

## Dependencies

Depends on VFS inode/page-cache/stat/setattr APIs, NFS protocol operation tables, pNFS, delegation logic, fscache/netfs hooks, NFS access/ACL/xattr/security-label helpers, RPC stats/metrics, lockd-related mount semantics, per-network namespace infrastructure, sysfs/proc support, and NFS page/read/write/direct caches.

## Risks

Attribute coherency is the main complexity. The code must reconcile server attributes, client dirty data, delegations, pNFS layoutcommit, out-of-order RPC replies, and weak cache consistency without corrupting size/change state. Mapping invalidation uses memory barriers and bit locks; weakening those races stale page-cache data. Inode identity checks must detect fileid/type changes and mark stale inodes. Initialization and teardown have many staged resources and must unwind in the correct order.
