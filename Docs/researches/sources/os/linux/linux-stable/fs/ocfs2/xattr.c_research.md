# File Research: sources/os/linux/linux-stable/fs/ocfs2/xattr.c

## Scope

This file implements OCFS2 extended attributes: VFS xattr handlers, inline-inode xattrs, external xattr blocks, indexed xattr bucket trees, large xattr value extent trees, refcount/reflink handling, security xattr initialization, ACL/security preallocation accounting, and full xattr teardown.

## Main Entry Points

- `ocfs2_listxattr()` lists inode-inline and external/block/tree xattrs under inode and xattr semaphores.
- `ocfs2_xattr_get_nolock()` and internal `ocfs2_xattr_get()` locate and return a named xattr from inline inode storage or external storage.
- `ocfs2_xattr_set()` is the normal create/replace/remove path, handling inode locking, xattr lookup, flag validation, refcount preparation, allocator reservation, journaling, truncate-log flushing, ctime update, and cleanup.
- `ocfs2_xattr_set_handle()` is the create-time path used by inode creation/security/ACL setup when transaction credits and allocators were reserved by the caller.
- `ocfs2_xattr_remove()` frees all xattr resources for inode teardown.
- `ocfs2_xattr_attach_refcount_tree()` and `ocfs2_reflink_xattrs()` integrate xattr value extents with OCFS2 reflink/refcount trees.
- Handler exports implement `user.*`, `trusted.*`, and `security.*`; POSIX ACL types are in the internal handler map through nop ACL handlers.

## Data Model

- Xattrs may live in three containers: inline at the end of the dinode, in a single external `ocfs2_xattr_block`, or in indexed xattr buckets addressed by an extent tree rooted in an xattr block.
- Small values up to `OCFS2_XATTR_INLINE_SIZE` are stored directly in the name/value area. Larger values are represented by `ocfs2_xattr_value_root`, an extent tree whose clusters contain value bytes.
- `ocfs2_xattr_bucket` wraps the fixed-size bucket buffer-head array. Bucket metadata includes sorted entries, free-start tracking, name/value byte count, and bucket-run count.
- `ocfs2_xa_loc` abstracts mutation of inode-inline, unindexed block, and bucket storage through `ocfs2_xa_loc_operations`. This is the central unifier for add/remove/reuse/store logic.

## Control Flow

- Lookup first searches inline inode xattrs when present, then external xattr storage if `i_xattr_loc` exists. Indexed blocks hash the xattr name, locate the matching extent record, binary-search bucket ranges, then linearly scan same-hash entries.
- Set prefers inode-inline storage. If there is no room, it falls back to external block storage. If an unindexed block fills, it is converted to an indexed xattr tree and existing entries are copied into a bucket.
- Mutation uses `ocfs2_xa_set()`: journal access, remove-or-prepare entry, allocate/truncate external value storage when needed, store local or external bytes, then dirty the owning storage.
- Bucket insertion handles sorted-by-hash entries, defragments bucket holes on ENOSPC, and allocates/splits buckets or clusters when needed.
- Indexed bucket growth can extend a contiguous extent, split a bucket, split a cluster, or move buckets into a new non-contiguous cluster while preserving hash range boundaries.
- Large external value changes grow or shrink the value extent tree. Shrink paths remove extents, update `xr_clusters`, drop/refcount clusters, update the xattr cluster cache, and schedule truncate-log/dealloc work.
- Refcounted xattrs are prepared before allocator locking to avoid deadlocks. Existing refcounted external values may be CoWed wholesale before overwrite, or metadata/credits are reserved for delete/truncate paths.
- Reflink copies inline/block/tree xattrs into the new inode, optionally filters security/ACL xattrs, recreates value trees when needed, and increases refcounts for every external value extent.

## Dependencies

- OCFS2 locking and metadata: inode locks, `ip_xattr_sem`, `ip_alloc_sem`, journal handles, dinode/xattr-block accessors, metadata ECC, truncate log, cached dealloc contexts, allocation contexts, extent trees, and refcount trees.
- Linux VFS/xattr/LSM: xattr handler callbacks, security initialization, capability checks for trusted xattrs, POSIX ACL visibility, idmapped set signatures, buffer heads, and inode ctime helpers.
- OCFS2 tree helpers: `ocfs2_find_leaf()`, `ocfs2_insert_extent()`, `ocfs2_remove_extent()`, `ocfs2_add_clusters_in_btree()`, `ocfs2_xattr_get_clusters()`, and refcount CoW/increase/decrease helpers.

## Invariants And Risks

- Bucket name/value records must not cross filesystem block boundaries; several helpers assert this when computing value roots.
- Bucket entries are sorted by `xe_name_hash`; same-hash entries must remain in the same bucket when splitting. Excessive same-hash collisions intentionally return `-ENOSPC`.
- Journal credit calculation is complex because one set operation can touch the inode, xattr block, buckets, xattr value extents, refcount tree, data clusters, metadata allocators, and truncate log.
- Error handling deliberately dirties containers after partial mutation so on-disk xattr headers remain structurally consistent. Some failures leak clusters rather than leave corrupt entries.
- Refcount/reflink paths depend on correct post-refcount bucket ECC recomputation and on avoiding allocator/refcount lock deadlocks.
- Inline xattr size validation protects against corrupted `i_xattr_inline_size` and entry counts before listing.
