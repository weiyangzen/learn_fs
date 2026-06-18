# File Research: sources/local-fs/btrfs-linux/fs/btrfs/backref.h

Public declarations and data structures for Btrfs backref walking and backref cache construction.

Key points:
- Defines `BTRFS_ITERATE_EXTENT_INODES_STOP` as a non-error early-stop signal for inode iteration callbacks.
- Defines `iterate_extent_inodes_t`, called with inode number, file offset, byte length, root id, and user context.
- `struct btrfs_backref_walk_ctx` is the main backref-walk context:
  - Target extent bytenr.
  - Data extent position filtering.
  - Flags to ignore position or skip inode lists.
  - Optional transaction/time-sequence.
  - Output `refs` and `roots` ulists.
  - Optional cache lookup/store callbacks.
  - Optional indirect-ref iterator, extent-item checker, and data-ref skip callback.
- `struct inode_fs_paths` groups a path object, fs root, and output path container.
- `struct btrfs_backref_share_check_ctx` caches sharedness checks:
  - Current/previous leaf bytenr.
  - Per-level path cache entries.
  - Small recent extent cache for repeated data extent bytenrs.
- Declares APIs for:
  - Extent lookup from logical address.
  - Tree backref iteration.
  - Extent-to-inode iteration.
  - Logical-to-inode iteration.
  - Inode-to-path conversion.
  - Finding all leaves/roots.
  - Data extent sharedness checks.
  - Prelim-ref cache initialization/teardown.
- Defines `struct prelim_ref`, the internal merged backref representation.
- Defines `struct btrfs_backref_iter` and helper `btrfs_backref_has_tree_block_info()`.
- Defines backref graph/cache structs:
  - `btrfs_backref_node`.
  - `btrfs_backref_edge`.
  - `btrfs_backref_cache`.
- Declares node/edge allocation, cleanup, cache release, add-tree-node, finish-link, and error-cleanup routines.
- `btrfs_backref_panic()` reports irrecoverable cache inconsistency.

Role in system:
- Provides the interface used by relocation, fiemap, qgroups, ioctl logical-inode lookup, and other code needing reference ancestry.
- Encodes the shared ownership/lifetime model for backref graph nodes and edges.
