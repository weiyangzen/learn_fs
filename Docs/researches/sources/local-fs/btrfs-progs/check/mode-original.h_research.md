# File Research: sources/local-fs/btrfs-progs/check/mode-original.h

## Scope

This header defines the in-memory record model used by the original Btrfs checker mode: extent records, inode records, root records, backrefs, shared-node caches, and error-bit constants.

## Public Data Structures

- `struct extent_backref`, `data_backref`, and `tree_backref` model extent-tree backrefs in rbtrees/lists.
- `struct extent_record` tracks one extent’s size, refs, generation, owner info, flags, duplicate records, and validation state.
- `struct inode_backref` and `struct inode_record` track inode refs, dir-item/index state, inode item state, file extent holes, nlink/nbytes/isize accounting, checksum state, mismatch dir hashes, and unaligned extents.
- `struct root_backref` and `struct root_record` track subvolume root ref/backref consistency and root ref counts.
- `struct root_item_record`, `root_item_info`, and `bad_item` preserve root item and bad-item metadata.
- `struct shared_node`, `ptr_node`, `block_info`, and `walk_control` support shared tree walking and per-node inode/root caches.
- `struct file_extent_hole` and `unaligned_extent_rec_t` represent extent holes and unaligned extent records.

## Error Constants

- `REF_ERR_*` bits classify missing, duplicate, mismatched, too-long, and root-ref/root-backref errors.
- `I_ERR_*` bits classify inode-item, orphan, dir-index, dir-item, file-extent, csum, link-count, inode-flag, hash, imode, generation, nlink, xattr, deprecated free-inode, and duplicate filename problems.
- `FLAG_UNSET` explicitly initializes `extent_record::flag_block_full_backref`.

## Dependencies

- Uses kernel rbtrees/lists, Btrfs tree constants, cache extents, and rbtree utility helpers.
- Provides the structural vocabulary for original-mode checker implementation files outside this group.

## Risks And Invariants

- The original mode depends on these records being merged and cross-referenced correctly; stale `found_*` or error bits can cause false repairs or missed corruption.
- Flexible trailing name buffers require exact allocation sizes.
- Extent and inode accounting fields distinguish on-disk refs from discovered refs; conflating them would hide metadata inconsistencies.
