# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_node.c

This file implements FUSE vnode-private state allocation, vnode lookup/creation, attribute-cache state transitions, file-size synchronization, and cached timestamp maintenance.

Key responsibilities:
- Defines `M_FUSEVN` allocation type for `struct fuse_vnode_data`.
- Tracks active FUSE vnode count through `fuse_node_count`.
- Defines global default `fuse_data_cache_mode = FUSE_CACHE_WT`.
- Exposes `vfs.fusefs.data_cache_mode`.
  - Retained mainly for old protocol/libfuse2 servers before per-mount protocol 7.23 cache negotiation.
  - Accepts uncached, write-through, and writeback values.
- Initializes vnode-private state in `fuse_vnode_init`.
  - Sets node id, handle list, cached attr mutex, default `vattr`, root flag, vnode type, `v_data`, cluster-write state, local modify timestamp, and node counter.
- Destroys vnode-private state in `fuse_vnode_destroy`.
  - Clears `v_data`.
  - Destroys attr mutex.
  - Asserts no open file handles remain.
  - Frees private data and decrements counter.
- Implements vnode hash comparison with `fuse_vnode_cmp`.
- Allocates or reuses vnodes in internal `fuse_vnode_alloc`.
  - Uses `vfs_hash_get` and `vfs_hash_insert`.
  - Rejects `VNON`.
  - Reuses existing vnode if node id and type match.
  - If type differs, marks stale vnode disappeared, calls `vgone`, and allocates replacement.
  - Chooses FIFO vnode ops for `VFIFO`, normal FUSE vnode ops otherwise.
  - Uses `insmntque`, async shared locking for async-read non-FIFO nodes, and `vn_set_state`.
- Publishes vnode lookup/creation through `fuse_vnode_get`.
  - Validates parent/child node id mismatch.
  - Warns when export-support filesystems return `attr.ino` different from `nodeid`.
  - Calls `fuse_vnode_alloc`.
  - Sets parent node id for directory children.
  - Enters namecache entries when `MAKEENTRY` and entry TTL are present.
  - Stores generation and increments FUSE lookup count except for dot/dotdot/root-like cases.
- Initializes vnode state on open in `fuse_vnode_open`.
  - Creates a VM object for regular files.
- Synchronizes locally dirty size to daemon in `fuse_vnode_savesize`.
  - Sends `FUSE_SETATTR` with `FATTR_SIZE`.
  - Uses an available write handle when possible.
  - Clears `FN_SIZECHANGE` and updates `last_local_modify` on success.
- Adjusts local vnode size in `fuse_vnode_setsize`.
  - Updates cached attrs.
  - Invalidates buffers when server-side growth indicates daemon changed size behind the kernel’s back.
  - Performs immediate pager/buffer resize under exclusive lock or defers through `vn_delayed_setsize`.
- Implements immediate size changes in `fuse_vnode_setsize_immediate`.
  - Shrink path calls `vtruncbuf`.
  - Clears stale data in the final partial block if cached.
  - Updates vnode pager size.
- Reads current size in `fuse_vnode_size`.
  - Uses cached dirty size when `FN_SIZECHANGE` is set.
  - Fetches daemon attrs when cache is invalid or size unknown.
- Manages timestamp dirty flags.
  - `fuse_vnode_undirty_cached_timestamps` clears dirty mtime/ctime and optionally atime.
  - `fuse_vnode_update` rounds timestamps to negotiated granularity, honors `MNT_NOATIME`, updates cached attrs, and sets dirty flags.
- Initializes/destroys node subsystem counter in `fuse_node_init` and `fuse_node_destroy`.

Integration points:
- Used by `fuse_internal.c` for lookup/create/getattr/setattr/cache updates.
- Used by `fuse_io.c` for file-size and timestamp updates.
- Depends on vnode operation vectors declared in `fuse_node.h`.
- Cooperates with VFS hash and namecache mechanisms.
- File-handle list is managed with `fuse_file.h`.

Notable risks and research hooks:
- `FN_DIRECTIO` is vnode-scoped, and the header comments identify that as a bug because direct I/O should be file-handle scoped.
- Reused inode numbers with changed types cause stale vnode disappearance and replacement; correctness depends on daemon entry TTL behavior.
- `fuse_vnode_get` warns but does not fail for `attr.ino != nodeid` unless parent/child node ids are invalid.
- Deferred setsize is used when the vnode is not exclusively locked, making lock mode central to size update behavior.
- Writeback cache and dirty size flags require careful ordering between `fuse_vnode_savesize`, writes, getattr, and lookup.
