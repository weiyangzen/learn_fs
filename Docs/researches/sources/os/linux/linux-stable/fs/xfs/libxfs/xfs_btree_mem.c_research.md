# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree_mem.c

## Role in the repository

`xfs_btree_mem.c` implements xfile-backed in-memory btree support. These btrees use the generic btree core with `XFS_BTREE_TYPE_MEM`, but their blocks live in an in-memory buffer target rather than on the filesystem device. This is primarily useful for online repair and rebuild workflows that construct temporary metadata indexes.

## Root and cursor callbacks

The file provides generic callbacks for memory btree operation tables:
- `xfbtree_set_root` updates the `struct xfbtree` root pointer and adjusts height by the supplied increment.
- `xfbtree_init_ptr_from_cur` copies the current memory btree root into a generic btree pointer.
- `xfbtree_dup_cursor` allocates a new generic cursor, copies common cursor state, shares the same `struct xfbtree`, and holds the cursor group reference if present.

These callbacks allow the generic code in `xfs_btree.c` to treat memory btrees like normal long-pointer btrees.

## Initialization and geometry

`xfbtree_init` initializes an empty memory btree:
- It requires a CRC-enabled filesystem.
- It requires long-format pointers.
- It stores the provided xfile buffer target.
- It computes leaf and node max/min records from `XMBUF_BLOCKSIZE`, the long CRC btree header length, and the concrete btree key/record sizes.
- It initializes height to one and creates an empty leaf root block through `xfbtree_init_leaf_block`.

`xfbtree_init_leaf_block` gets the first xfile-backed buffer, initializes it as a level-zero btree block with owner information, releases it, and records the root pointer.

`xfbtree_rec_bytes` returns the payload space available for records after the long CRC-format header. This is the basis for the max record calculations.

`xfbtree_destroy` drains the memory buffer target, releasing all resources associated with the xfile-backed btree.

## Allocation and free behavior

`xfbtree_alloc_block` allocates monotonically increasing pseudo block numbers from `xfbtree->highest_bno`. It verifies the block address fits the xfile buffer target with `xfbtree_verify_bno`; if not, it returns success with `stat = 0` so the generic btree core sees allocation failure without a direct errno.

`xfbtree_free_block` only decrements `highest_bno` when freeing the most recently allocated block. It does not maintain a free-space structure for arbitrary block reuse, which matches the temporary rebuild use case.

`xfbtree_get_minrecs` and `xfbtree_get_maxrecs` return the precomputed leaf or node fanout, selecting `maxrecs[0]/minrecs[0]` for leaves and `maxrecs[1]/minrecs[1]` for internal levels.

## Transaction commit and cancel handling

Memory btrees use regular transaction attachment to collect buffer pointers and avoid deadlocks, but their buffers must not commit through the normal filesystem log because the btree is temporary.

`xfbtree_buf_match` identifies transaction log items that are buffer log items for the memory btree's buffer target.

`xfbtree_trans_commit` walks transaction items:
- Non-xfbtree dirty items are remembered so the transaction dirty flag can be restored correctly.
- Xfbtree buffers are detached from the transaction.
- Each detached buffer is finalized immediately through `xmbuf_finalize`.
- Buffers are released even if verification/finalization reports an error.
- The transaction dirty bit is reset according to remaining non-xfbtree dirty items.

`xfbtree_trans_cancel` similarly detaches and releases xfbtree buffers without undoing changes. Its comment makes the lifetime requirement explicit: callers must not access the btree again after canceling changes this way.

## Important invariants

- Memory btrees require CRC format and long pointers.
- Blocks are addressed by `xfbno_t` values converted to/from disk addresses with the helpers in `xfs_btree_mem.h`.
- Memory btree allocation is append-style with only top-of-stack free rollback.
- Transaction commit/cancel paths remove all ephemeral btree buffers from the transaction so they do not enter the normal metadata log.
