# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree_mem.h

## Role in the repository

`xfs_btree_mem.h` declares the in-memory xfile-backed btree interface used by online repair and other temporary btree users. It provides the address type, address conversion helpers, the `struct xfbtree` header, and function declarations enabled by `CONFIG_XFS_BTREE_IN_MEM`.

## Addressing model

The file defines:
- `xfbno_t` as a 64-bit xfile btree block number.
- `XFBNO_BLOCKSIZE` as `XMBUF_BLOCKSIZE`.
- `XFBNO_BBSHIFT` and `XFBNO_BBSIZE` for conversion between xfile btree blocks and 512-byte basic block units.
- `xfbno_to_daddr` and `xfs_daddr_to_xfbno` to convert between `xfbno_t` and `xfs_daddr_t`.

This lets the generic buffer and btree code address xfile-backed blocks through the same disk-address shaped APIs used for real metadata buffers.

## `struct xfbtree`

`struct xfbtree` stores the persistent in-memory btree header:
- The buffer cache target backing the xfile.
- The highest block number allocated so far.
- The owner value written into btree blocks.
- The generic root pointer and number of levels.
- Leaf and node min/max record counts.

The structure is intentionally small; the actual btree blocks live in the xfile buffer target.

## Conditional API

When `CONFIG_XFS_BTREE_IN_MEM` is enabled, the header declares:
- Block verification: `xfbtree_verify_bno`.
- Generic btree callbacks: `xfbtree_set_root`, `xfbtree_init_ptr_from_cur`, `xfbtree_dup_cursor`.
- Fanout callbacks: `xfbtree_get_minrecs`, `xfbtree_get_maxrecs`.
- Block allocation/free callbacks: `xfbtree_alloc_block`, `xfbtree_free_block`.
- Lifecycle: `xfbtree_init`, `xfbtree_destroy`.
- Transaction detachment: `xfbtree_trans_commit`, `xfbtree_trans_cancel`.

When the option is disabled, `xfbtree_verify_bno` is defined as false, preventing accidental successful verification of memory btree addresses.

## Important invariants

- Callers must provide a buffer target and owner before initialization.
- Memory btree users must match the generic btree op table to long-pointer CRC btree semantics.
- The address conversion helpers assume xfile block sizes are powers compatible with basic block addressing.
