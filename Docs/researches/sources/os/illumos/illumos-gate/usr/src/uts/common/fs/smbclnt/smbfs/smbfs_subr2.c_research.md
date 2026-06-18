# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_subr2.c

## Purpose
SMBFS client vnode/node cache implementation and supporting utilities. It manages `smbnode` lifecycle, per-mount AVL lookup by remote path, free-list recycling, node destruction, cache pruning, flushing, direct I/O state, and module-level node-cache initialization.

## Core Design
- Uses a per-mount AVL tree keyed by full remote path (`n_rpath`, `n_rplen`).
- Replaces older global hash-chain style while retaining some “hash” naming in fields/functions.
- Maintains a global smbnode free list for reusable inactive nodes.
- Keeps vnode reference counts from dropping below one while nodes are cached/free-listed.
- Lock ordering is documented as:
  - AVL tree lock -> vnode lock
  - AVL tree lock -> freelist lock

## Key Functions
- `smbfs_node_findcreate(...)`
  - Builds a remote path from directory path, optional separator, and name.
  - Looks up or creates an `smbnode`.
  - Applies attributes when real `smbfattr` is provided.
  - Uses `smbfs_fattr0` as a sentinel to force creation without real attributes.
- `make_smbnode(...)`
  - Allocates or recycles an smbnode.
  - Drops/reacquires the AVL lock around allocation.
  - Rechecks for races before inserting into the AVL tree.
  - Initializes vnode ops, mount reference, locks, owner/group defaults, path string, and inode hash.
- `smbfs_addfree(...)`
  - Either places an inactive node on the free list or destroys it.
  - Destroys immediately when unhashable, errored, unmounted, or over node limit if no references remain.
- `sn_hashfind(...)`
  - Finds a node by path in the mount AVL tree.
  - Removes it from the free list or takes a vnode hold before returning.
- `smbfs_attrcache_prune(...)`
  - Walks the AVL tree after a node and invalidates cached attributes for descendants.
  - Handles both normal child separator `\` and XATTR separator `:`.
- `smbfs_check_table(...)`
  - Checks for active/busy vnodes during unmount.
  - Considers non-free-listed nodes, dirty cached pages, and extra `r_count` references.
- `smbfs_destroy_table(...)`
  - Removes inactive nodes from a mount’s AVL tree during unmount.
  - Preserves busy nodes in a temporary AVL tree.
- `smbfs_rflush(...)`
  - Finds vnodes with dirty or mapped pages and issues `VOP_PUTPAGE`.
- `smbfs_directio(...)`
  - Enables/disables direct I/O.
  - Flushes dirty cached pages before enabling direct mode.
- `smbfs_newnum()` / `smbfs_newname(...)`
  - Generate unique temporary unlink/rename names like `~$smbfs%08X`.
- `smbfs_subrinit()` / `smbfs_subrfini()`
  - Create/destroy the smbnode cache and global locks.
  - Allocate a unique major device number and initialize minor counter.
- `smbfs_kmem_reclaim(...)`
  - Frees reusable nodes from the smbnode free list under memory pressure.

## Important Interactions
- `smbfs_vfsops.c` initializes one AVL tree per mount and destroys it during unmount.
- `smbfs_vnops.c` relies on node identity for lookups, creates, renames, removes, and XATTR fake directories.
- Attribute cache pruning is critical after rename/delete so stale descendant nodes are not trusted.

## Notes
- Path identity is central: `n_rpath` is both lookup key and inode-hash input.
- The code is race-aware around node allocation, vnode refs, pageout, and unmount.
