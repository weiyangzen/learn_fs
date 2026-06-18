# File Research: sources/local-fs/ocfs2-tools/libocfs2/extents.c

Purpose: extent block I/O, byte swapping, extent iteration, and block iteration.

Key responsibilities:
- Swaps extent lists and extent blocks between disk and CPU byte order.
- Reads and writes extent blocks with block-range, ECC, signature, and basic count validation.
- Iterates inode, xattr, and dx-root extent trees.
- Calls user callbacks for interior and leaf records depending on traversal flags.
- Maintains `i_last_eb_blk` during full inode iteration.
- Iterates physical data blocks represented by leaf extents.

Important APIs:
- `ocfs2_swap_extent_list_from_cpu()`, `ocfs2_swap_extent_list_to_cpu()`
- `ocfs2_swap_extent_block_from_cpu()`, `ocfs2_swap_extent_block_to_cpu()`
- `ocfs2_read_extent_block_nocheck()`, `ocfs2_read_extent_block()`, `ocfs2_write_extent_block()`
- `ocfs2_extent_iterate_xattr()`
- `ocfs2_extent_iterate_inode()`
- `ocfs2_extent_iterate_dx_root()`
- `ocfs2_extent_iterate()`
- `ocfs2_block_iterate_inode()`, `ocfs2_block_iterate()`

Core invariants:
- Extent block signature must match `OCFS2_EXTENT_BLOCK_SIGNATURE`.
- `l_next_free_rec` must not exceed `l_count` after checked reads.
- Iteration skips a leftmost empty leaf record.
- Inode iteration rejects invalid inodes, super/local-alloc/chain inodes, and inline-data inodes.
- Full inode iteration can update stale `i_last_eb_blk` and clear the last leaf’s `h_next_leaf_blk`.

Dependencies:
- Uses low-level block I/O, metadata ECC helpers, inode read/write, and extent-tree constants/macros.
- Uses callback flags such as `OCFS2_EXTENT_FLAG_DEPTH_TRAVERSE`, `OCFS2_EXTENT_FLAG_DATA_ONLY`, and block append behavior.

Notable behavior:
- `update_leaf_rec()` and `update_eb_rec()` are stubs returning 0; changed records are written through surrounding block/root write paths rather than local per-record adjustment hooks.
- `ocfs2_extent_iterate_dx_root()` has write-back logic disabled under `#if 0`, so dx-root iteration can mark changed in memory but does not persist root changes here.
- `ocfs2_block_iterate_inode()` expands extents into per-block callbacks and stops at inode size unless append iteration is requested.
