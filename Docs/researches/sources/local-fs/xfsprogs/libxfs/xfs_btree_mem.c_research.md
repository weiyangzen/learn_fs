# File Research: sources/local-fs/xfsprogs/libxfs/xfs_btree_mem.c

## Purpose

`xfs_btree_mem.c` implements xfile-backed in-memory btree support. These btrees use the generic btree engine with `XFS_BTREE_TYPE_MEM`, storing blocks in an in-memory buffer target rather than filesystem metadata blocks.

This support is used by repair and staging workflows that need temporary btree indexes whose contents can be discarded after the operation.

The file is byte-identical to the Linux-stable copy in this repository.

## Root and Cursor Operations

The file provides generic ops suitable for concrete memory-backed btrees:

- `xfbtree_set_root`: updates the in-memory root pointer and height.
- `xfbtree_init_ptr_from_cur`: initializes traversal from `xfbtree->root`.
- `xfbtree_dup_cursor`: allocates a duplicate cursor, copies flags and height, shares the `xfbtree`, and holds the group reference if present.

These functions assert that the cursor type is `XFS_BTREE_TYPE_MEM`.

## Lifecycle

`xfbtree_init` prepares an empty in-memory btree:

- requires a CRC-enabled filesystem;
- requires long btree pointers;
- clears the `struct xfbtree`;
- attaches the caller-provided memory buffer target;
- computes min/max records for leaf and node blocks from `XMBUF_BLOCKSIZE`;
- starts at height 1;
- initializes an empty leaf block as the root.

Callers must set `xfbt->owner` before initialization.

`xfbtree_destroy` drains the memory buffer target.

## Block Allocation

`xfbtree_alloc_block` allocates monotonically increasing xfile block numbers using `highest_bno`. It verifies the resulting address against the memory buffer target before returning it as a long btree pointer.

`xfbtree_free_block` observes freed block numbers and decrements `highest_bno` only when the highest-numbered block is freed. It does not maintain a general free list.

This allocation model is simple and sufficient for temporary btrees.

## Geometry

`xfbtree_get_minrecs` and `xfbtree_get_maxrecs` return leaf or node geometry from `xfbtree->minrecs` and `xfbtree->maxrecs`.

`xfbtree_rec_bytes` computes usable record space by subtracting the long-format CRC btree header from the memory buffer block size.

## Transaction Commit and Cancel

Temporary memory btrees still attach buffers to xfs transactions to coordinate locking and updates. They cannot rely on normal transaction commit persistence because the backing xfile is ephemeral.

`xfbtree_trans_commit`:

- scans transaction log items;
- finds buffer log items belonging to the `xfbtree` target;
- detaches those buffers from the transaction;
- finalizes them to the xfile with `xmbuf_finalize`;
- releases all matching buffers even if one finalize fails;
- recalculates the transaction dirty flag for remaining non-xfbtree items.

`xfbtree_trans_cancel` similarly detaches and releases all xfbtree buffers but does not undo changes. Callers must not access the btree after cancellation.

## Dependencies

The implementation depends on:

- `xfs_btree.c` for generic btree operation;
- `xfs_btree_mem.h` for `struct xfbtree` and address conversion;
- xfsprogs `xfile` and `buf_mem` support;
- transaction item lists and buffer log item plumbing;
- tracepoints for create, init, alloc/free, commit, and cancel events.
