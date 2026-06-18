# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree_mem.h

## Purpose

`xfs_btree_mem.h` declares the in-memory XFS btree wrapper type and callback helpers used to adapt generic btree operations to `xmbuf`-backed ephemeral btrees.

## Key Definitions

`xfbno_t` is the fake block-number type for memory btrees.

The header defines conversions between fake btree block numbers and disk-address units:

- `xfbno_to_daddr`
- `xfs_daddr_to_xfbno`

The fake block size is tied to `XMBUF_BLOCKSIZE`, with sector-size conversion constants.

## `struct xfbtree`

`struct xfbtree` stores:

- The in-memory buffer target.
- The highest fake block number written.
- The owner value stored in btree block headers.
- The root btree pointer.
- The current tree height.
- Precomputed max/min records for leaf and node blocks.

This structure is the persistent state shared by cursors over an in-memory btree.

## Exported Interface

When `CONFIG_XFS_BTREE_IN_MEM` is enabled, the header declares:

- Block validation: `xfbtree_verify_bno`.
- Root callbacks: `xfbtree_set_root`, `xfbtree_init_ptr_from_cur`.
- Cursor callback: `xfbtree_dup_cursor`.
- Geometry callbacks: `xfbtree_get_minrecs`, `xfbtree_get_maxrecs`.
- Allocation callbacks: `xfbtree_alloc_block`, `xfbtree_free_block`.
- Lifecycle: `xfbtree_init`, `xfbtree_destroy`.
- Transaction integration: `xfbtree_trans_commit`, `xfbtree_trans_cancel`.

When the option is disabled, `xfbtree_verify_bno` is stubbed to false.

## Integration Points

Concrete memory-backed btree operation tables use these functions as their generic `xfs_btree_ops` callbacks. Online repair code owns the `struct xfbtree`, supplies an `xfs_buftarg`, and uses the transaction helpers to keep ephemeral btree buffers out of normal log commit paths.

## Important Invariants

- Callers must set owner/target context before initialization as documented.
- The btree uses `xmbuf` block sizing.
- Memory btree blocks are addressed as long btree pointers.
- The disabled-config stub intentionally prevents accidental validation success.
