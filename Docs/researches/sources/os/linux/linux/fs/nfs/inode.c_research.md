# File Research: sources/os/linux/linux/fs/nfs/inode.c

## Purpose
Implements NFS inode and superblock support: inode cache allocation, filehandle-based inode lookup, attribute cache validation/update, open and lock contexts, fscache hooks, revalidation, data-cache invalidation, workqueues, per-net initialization, and module init/exit.

## Inode Lifecycle
- `nfs_alloc_inode()` allocates `struct nfs_inode` from `nfs_inode_cachep`, initializes NFSv4/netfs fields, and returns embedded VFS inode.
- `nfs_free_inode()` frees out-of-order state and the slab object.
- `nfs_clear_inode()` clears ACL/access/fscache state and asserts no writebacks/open files.
- `nfs_evict_inode()` truncates pages, clears the inode, and calls NFS cleanup.
- Slab cache is created/destroyed by `nfs_init_inodecache()` and `nfs_destroy_inodecache()`.

## Filehandle-Based Inode Lookup
`nfs_fhget()` is the central inode acquisition path:
- Uses filehandle plus fileid/type matching, not just inode number.
- Handles mounted-on fileid.
- Initializes new inodes according to type: regular, directory, symlink, special.
- Sets operation tables from protocol ops.
- Initializes pagecache ops, regular-file commit state, directory state, mountpoint/referral automount behavior, timestamps, ownership, blocks, cache validity flags, security labels, and fscache.
- Existing inodes are refreshed through `nfs_refresh_inode()`.

`nfs_ilookup()` performs lookup without allocation.

## Attribute Cache and Invalidation
The file maintains detailed cache-validity flags:
- Attribute fields: mode, owner/group, nlink, size, blocks, atime/mtime/ctime/btime, change attr.
- Data/access/ACL/xattr invalidation.
- Revalidation forcing and stale marking.

`nfs_set_cache_invalid()` respects delegated attributes, invalidates fscache for data changes, uses release/acquire memory ordering against mapping invalidation, and clears out-of-order tracking when appropriate.

`nfs_zap_caches()`/`nfs_zap_mapping()` invalidate local metadata/data caches.

## Revalidation and Mapping Invalidation
`__nfs_revalidate_inode()` syncs pNFS layout state for regular files, fetches attributes through protocol `getattr`, handles softreval timeouts, marks stale inodes, refreshes attributes, clears ACL invalidation, and updates security labels.

`nfs_revalidate_mapping()` revalidates inode metadata when needed and calls `nfs_clear_invalid_mapping()`.

`nfs_clear_invalid_mapping()` serializes pagecache invalidation with the `NFS_INO_INVALIDATING` bit, clears `NFS_INO_INVALID_DATA` under lock before invalidating, syncs regular mappings, invalidates pages, and wakes waiters.

## Attribute Update Ordering
A global attribute generation counter prevents older RPC replies from overwriting newer inode state. Key helpers:
- `nfs_fattr_init()`
- `nfs_fattr_set_barrier()`
- `nfs_inode_attrs_cmp*()`
- `nfs_refresh_inode_locked()`

The code also tracks out-of-order change-attribute gaps (`nfsi->ooo`) so stale/interleaved replies do not corrupt cache state.

## Metadata Updates
`nfs_setattr()` handles VFS setattr:
- Blocks direct I/O for regular files.
- Validates truncates.
- Optimizes delegated atime/mtime updates.
- Flushes dirty data before server setattr.
- Calls protocol `setattr()`, truncates last folio if size changed, and refreshes attributes.

`nfs_setattr_update_inode()` and post-op update helpers combine local updates, weak cache consistency data, invalidation flags, and full inode refresh.

`nfs_update_inode()` is the main attribute application engine. It validates fileid/type, updates fsid, delegation-adjusted attrs, weak cache consistency, pNFS layoutcommit interaction, change attr, timestamps, size, mode, owner/group, nlink, blocks, attr timeout backoff, and invalidation flags. On identity/type mismatch it marks the inode stale.

## Open and Lock Contexts
- `alloc_nfs_open_context()` creates per-open context with dentry, creds, mode, lock context, localio state, and superblock active ref.
- `nfs_file_set_open_context()` attaches context to a file and inode open list.
- `nfs_file_clear_open_context()` clears file private data, invalidates pages after write errors, and drops the context synchronously.
- `nfs_find_open_context()` finds matching open context by credential and mode.
- `nfs_get_lock_context()` and `nfs_put_lock_context()` manage per-open lock-owner contexts with RCU and inode locking.

`nfs_close_context()` revalidates change/size on synchronous write close when close-to-open consistency requires it.

## Stat and File Attributes
`nfs_getattr()` implements statx behavior:
- Honors `AT_STATX_DONT_SYNC` and `AT_STATX_FORCE_SYNC`.
- Flushes writes before ctime/mtime/change-cookie queries.
- Avoids atime revalidation under noatime/nodiratime.
- Revalidates only requested stale attributes.
- Fills stat fields, NFS-compatible inode number, change cookie, btime, and DIO alignment values.

`nfs_fileattr_get()` reports case-insensitive/case-nonpreserving capabilities as file attributes.

## Global Initialization
`init_nfs_fs()` initializes:
- Optional keyring.
- NFS sysfs.
- Per-net subsystem.
- `nfsiod` and optional `nfslocaliod` workqueues.
- procfs support.
- NFS page/read/write/direct caches.
- Inode cache.
- NFS filesystem registration.

`exit_nfs_fs()` tears these down in reverse. The module exports `enable_ino64` to control user-visible 64-bit inode numbers.

## Research Notes
This is foundational NFS client infrastructure. It coordinates VFS inode identity, cache coherency, fscache, pNFS layoutcommit interactions, open context lifetime, workqueue/module setup, and stat behavior. Bugs here can affect all NFS protocol versions and layout drivers.
