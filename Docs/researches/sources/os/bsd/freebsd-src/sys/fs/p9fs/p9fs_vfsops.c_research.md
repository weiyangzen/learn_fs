# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9fs_vfsops.c

This file implements p9fs mount-level VFS operations and vnode creation/common lookup support.

Initialization:
- Creates UMA zones for p9fs nodes, getattr buffers, setattr buffers, I/O buffers, and pbufs.
- Calls `p9_init_zones()` for client-layer fid/request/buffer zones.
- Destroys all zones in `p9fs_uninit()`.

Mount/unmount:
- `p9_mount()` validates options (`from`, `trans`, `access`, `msize`), extracts the mount tag, allocates `struct p9fs_mount`, initializes the session/root node, creates the 9P session, installs mount flags, and marks the mount local/shared-lookup capable.
- `p9fs_mount()` supports a minimal update path that can clear read-only if remounted writable, otherwise calls `p9_mount()`.
- `p9fs_unmount()` begins disconnect, repeatedly flushes vnodes with optional force close, closes the session, frees mount data, and restores transport status if unmount fails.

Vnode/node handling:
- `p9fs_dispose_node()` detaches vnode data, releases parent vnode references, frees inode names and non-root node storage.
- `p9fs_destroy_node()` destroys fid-list mutexes then disposes the node.
- `p9fs_node_cmp()` compares vnode qid path, and for non-root also qid mode/version.
- `p9fs_vget_common()` is the shared vnode lookup/create path:
  - Hashes by qid path.
  - Searches the vnode hash with `p9fs_node_cmp()`.
  - Reloads stats for existing non-root vnodes and drops stale deleted nodes.
  - Allocates a vnode and node if needed.
  - Adds the initial fid to the node.
  - Records parent/session/name metadata.
  - Inserts into mount queue and vnode hash.
  - Adds new nodes to the session node list and marks them constructed.

Other VFS operations:
- `p9fs_root()` gets a fid for the root, falling back to the mount fid during disconnect, and returns the root vnode through `p9fs_vget_common()`.
- `p9fs_statfs()` gets root fid, calls `p9_client_statfs()`, and fills FreeBSD `statfs`, capping block size at `PAGE_SIZE`.
- `p9fs_fhtovp()` is unsupported and returns `EINVAL`.

Research-relevant risks:
- `p9fs_vget_common()` has complex cleanup behavior around `insmntque()`, stale vnode removal, reload failures, and duplicate hash insertion.
- `p9fs_statfs()` returns success even if `p9_client_statfs()` fails, setting only fallback block sizes.
- `p9_mount()` stores `mount_tag` as the mount option buffer pointer rather than duplicating it.
- The filesystem is registered as jail-capable with `VFS_SET(p9fs_vfsops, p9fs, VFCF_JAIL)`.
