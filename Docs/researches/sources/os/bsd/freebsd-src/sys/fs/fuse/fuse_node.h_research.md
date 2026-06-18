# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_node.h

This header defines FreeBSD FUSE vnode-private state, vnode flags, attr-cache locking helpers, fid layout, and vnode helper APIs.

Key flags:
- `FN_REVOKED`: vnode has disappeared/revoked.
- `FN_FLUSHINPROG` / `FN_FLUSHWANT`: serialized buffer invalidation state.
- `FN_SIZECHANGE`: locally dirty size not yet sent to daemon.
- `FN_DIRECTIO`: vnode bypasses data cache; comment notes this should be per file handle.
- `FN_PARENT_NID`: `parent_nid` is valid.
- `FN_ATIMECHANGE`, `FN_MTIMECHANGE`, `FN_CTIMECHANGE`: dirty cached timestamps.
- `FN_DELAYED_TRUNCATE`: delayed setsize should truncate.

Key structures:
- `struct fuse_vnode_data`
  - Immutable node id and vnode type.
  - Generation number.
  - Parent node id protected by vnode lock.
  - List of open `fuse_filehandle` objects.
  - Cached attr mutex.
  - Attr cache timeout and entry cache timeout.
  - `last_local_modify` timestamp for ordering local mutations against daemon attrs.
  - Cached `struct vattr`.
  - FUSE lookup reference count.
  - Misc flags.
  - Clustered-write state.
- `struct fuse_fid`
  - Filehandle layout for export/NFS-style lookup: length, padding, generation, node id.

Important macros and inline helpers:
- `VTOFUD` and `VTOI` map vnode to FUSE private state and node id.
- `CACHED_ATTR_LOCK` and `CACHED_ATTR_UNLOCK` lock the attr mutex only when the vnode lock is not exclusive.
- `ASSERT_CACHED_ATTRS_LOCKED` validates attr-cache locking.
- `fuse_vnode_attr_cache_valid` compares attr timeout to current monotonic time.
- `VTOVA` returns cached attrs only when valid.
- `fuse_vnode_clear_attr_cache` clears attr timeout.
- `fuse_vnode_hash` hashes node ids for `vfs_hash`.
- `fuse_vnode_setparent` records parent node id for directory children or clears parent tracking.

Declared APIs:
- vnode comparison and lookup/creation:
  - `fuse_vnode_cmp`
  - `fuse_vnode_get`
- vnode state lifecycle:
  - `fuse_vnode_open`
  - `fuse_vnode_destroy`
  - `fuse_node_init`
  - `fuse_node_destroy`
- size management:
  - `fuse_vnode_size`
  - `fuse_vnode_savesize`
  - `fuse_vnode_setsize`
  - `fuse_vnode_setsize_immediate`
- timestamp and attr state:
  - `fuse_vnode_undirty_cached_timestamps`
  - `fuse_vnode_update`

Integration points:
- Included by internal, I/O, IPC, VFS, and vnode-op code.
- Depends on file-handle declarations from `fuse_file.h`.
- Exposes vnode operation vectors `fuse_fifoops` and `fuse_vnops`.

Notable risks and research hooks:
- Correct use of `CACHED_ATTR_LOCK` depends on holding some vnode lock before entry.
- `nlookup` is the kernel-side accounting for `LOOKUP` minus `FORGET`; mismatches can leak daemon references.
- Parent node id is valid only for directories and only when `FN_PARENT_NID` is set.
- Attr cache validity and dirty flags interact: dirty size/timestamps should not be overwritten by stale daemon responses.
