# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree_mem.c

## Purpose

`xfs_btree_mem.c` implements the generic-btree adapter for in-memory XFS btrees backed by `xmbuf` buffer targets. These btrees are used by online repair and staging workflows that need btree semantics without committing intermediate state to filesystem metadata.

The file is compiled when in-memory btree support is enabled and provides root management, block allocation/freeing, geometry, cursor duplication, initialization, destruction, and special transaction commit/cancel handling.

## Main Responsibilities

- Store and update the in-memory btree root in `struct xfbtree`.
- Duplicate memory-btree cursors.
- Initialize an empty CRC-format long-pointer btree in an `xmbuf` target.
- Calculate min/max records per block from `XMBUF_BLOCKSIZE`.
- Allocate monotonically increasing fake block numbers.
- Free only the most recently allocated fake block by reducing `highest_bno`.
- Detach in-memory btree buffers from transactions during commit/cancel.
- Finalize dirty in-memory buffers directly to the backing xfile on commit.

## Root and Cursor Handling

`xfbtree_set_root` copies the new root pointer into `xfbt->root` and adjusts `xfbt->nlevels`.

`xfbtree_init_ptr_from_cur` initializes traversal from `xfbt->root`.

`xfbtree_dup_cursor` allocates a new generic btree cursor, copies flags, height, and `xfbtree` pointer, and holds the cursor group if present. It does not duplicate persistent root state because the root lives in the shared `struct xfbtree`.

## Initialization

`xfbtree_init` requires:

- The mount must support CRC metadata.
- The concrete btree must use long pointers.
- The caller must have set `xfbt->owner`.
- The caller supplies an `xfs_buftarg` backed by in-memory xfile storage.

It clears the `xfbtree`, records the target, computes leaf and node fanout from block size minus long CRC btree header length, sets `nlevels` to one, and creates an empty leaf block as the root.

`xfbtree_init_leaf_block` obtains an in-memory buffer for block zero, initializes it as a btree leaf with zero records, releases it, and stores the root pointer.

## Block Allocation and Freeing

`xfbtree_alloc_block` assigns the next `highest_bno`, verifies that the `xmbuf` target can represent the block address, stores it as a big-endian long pointer, and reports success through `stat`.

`xfbtree_free_block` only decrements `highest_bno` if the freed block is the most recently allocated block. It does not perform general free-space management, so allocation is append-like.

## Record Geometry

`xfbtree_get_minrecs` and `xfbtree_get_maxrecs` return precomputed leaf or node fanout from `xfbt->minrecs[level != 0]` and `xfbt->maxrecs[level != 0]`.

This makes in-memory btrees compatible with generic balancing and bulk-loading code.

## Transaction Commit and Cancel

In-memory btree buffers cannot be committed through the normal filesystem log because they are ephemeral repair data. The file therefore scans transaction log items for buffer items whose target matches `xfbt->target`.

`xfbtree_trans_commit`:

- Finds matching buffer log items.
- Detaches them from the transaction with `xmbuf_trans_bdetach`.
- Finalizes each buffer to the xfile with `xmbuf_finalize`.
- Releases each buffer.
- Preserves the transaction dirty flag only if non-xfbtree items remain dirty.
- Continues detaching all xfbtree buffers even if one finalize fails.

`xfbtree_trans_cancel`:

- Detaches and releases xfbtree buffers without undoing changes.
- Recomputes the transaction dirty flag from remaining non-xfbtree items.
- Documents that callers must not access the btree after cancel because changes are not rolled back.

## Integration Points

This file plugs into `xfs_btree_ops` callbacks for memory btrees:

- `set_root`
- `init_ptr_from_cur`
- `dup_cursor`
- `alloc_block`
- `free_block`
- `get_minrecs`
- `get_maxrecs`

It also depends on `xfs_buf_mem`/`xmbuf` APIs, transaction item lists, buffer log items, tracing, and generic btree block initialization.

## Important Invariants

- In-memory btrees use long-format CRC btree blocks only.
- Fake block numbers convert to disk addresses through `xfbno_to_daddr`.
- `xfbt->target` must be an in-memory buffer target.
- Commit/cancel must remove all xfbtree buffers from a transaction before normal transaction processing continues.
- Cancel does not restore prior btree state.
