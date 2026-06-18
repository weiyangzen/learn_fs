# File Research: sources/local-fs/kdave-linux/fs/btrfs/btrfs_inode.h

This header defines the in-memory Btrfs inode structure, inode runtime flags, key inline helpers, and function prototypes for inode, delalloc, csum, encoded IO, directory, orphan, and locking operations.

Runtime flags:
- Cover close/writeback behavior, dummy/defrag state, async extents, full fsync requirements, property/xattr cache bits, no-delalloc-flush deadlock avoidance, verity-in-progress, free-space inode tagging, COW write error handling, and root-stub directory inodes.
- Several comments document required locking, especially `BTRFS_INODE_NEEDS_FULL_SYNC`, which must be set under VFS inode locking or equivalent exclusion.

`struct btrfs_inode` contents:
- Embeds ownership through `root` and, on 32-bit systems, an explicit 64-bit `objectid`.
- Stores compression properties, defrag compression controls, and inode flags.
- Uses `lock` for transaction/log counters, delalloc counters, outstanding extents, csum bytes, disk size, and private file data.
- Contains `extent_tree` for extent maps and `io_tree` for range state.
- Optionally tracks file extent item coverage through `file_extent_tree` when holes must be represented.
- Has `log_mutex` for tree-log operations.
- Tracks ordered extents with `ordered_tree_lock`, rb-tree root, and last node.
- Maintains delalloc inode list membership, runtime flags, full generation, transaction/log generation fields, delayed inode node, block reserve, delayed iput list, mmap lock, and embedded VFS inode.
- Uses unions to reuse fields by inode type: file delalloc counters vs directory log indexes, defrag bytes vs relocation block group start, index counter vs csum bytes, reflink transaction vs root-stub ref root id.

Key inline helpers:
- `BTRFS_I()` is a type-checked const-preserving container conversion from VFS inode to Btrfs inode.
- `btrfs_inode_hash()` hashes inode objectid with root objectid.
- `btrfs_ino()` preserves full inode numbers on 32-bit systems and handles root stubs specially.
- `btrfs_get_inode_key()` and `btrfs_set_inode_number()` bridge in-memory inode identity to B-tree keys.
- `btrfs_i_size_write()` updates both VFS i_size and Btrfs `disk_i_size`.
- `btrfs_is_free_space_inode()` tags special free-space-cache inodes, which are relevant to block group cache writeback.
- `btrfs_mod_outstanding_extents()` updates outstanding extent accounting and traces normal inodes.
- `btrfs_set_inode_last_sub_trans()`, `btrfs_set_inode_full_sync()`, and `btrfs_inode_in_log()` maintain fsync/logging state.
- `btrfs_inode_can_compress()` rejects compression for NODATACOW/NODATASUM.
- `btrfs_update_inode_mapping_flags()` controls stable write requirements based on checksumming.
- `btrfs_set_inode_mapping_order()` configures folio order for data inodes under experimental support.

Declared operation groups:
- Checksumming: metadata block checksums and data checksum verification.
- NOCOW: `can_nocow_extent()`, which interacts with block group NOCOW writer tracking.
- Directory/subvolume mutation: lookup, unlink, add link, delete subvolume, inode index allocation.
- Delalloc: start delalloc for roots/snapshots, set/clear/merge/split delalloc extent state.
- Inode lifecycle: allocate, destroy, free, drop, evict, iget, cache init/destroy.
- Extent and IO: get extent, preallocation, delalloc writeback, writepage COW fixup, encoded read/write.
- Transaction updates and cleanup: update inode, orphan add/cleanup, delayed iputs, inode byte accounting.
- Locking: `btrfs_inode_lock()` and `btrfs_inode_unlock()` with shared, try, and mmap lock modes.

Relationship to the other files in this group:
- Includes `block-rsv.h` because each inode embeds a `struct btrfs_block_rsv`.
- Free-space inodes are used by block group old space-cache persistence in `block-group.c`.
- NOCOW declarations depend on block group read-only and NOCOW writer coordination.
- Delalloc and inode block reserves feed the metadata reservation machinery implemented in `block-rsv.c`.
