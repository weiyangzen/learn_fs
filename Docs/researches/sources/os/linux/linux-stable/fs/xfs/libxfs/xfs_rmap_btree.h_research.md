# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rmap_btree.h

## Scope

Header for reverse-map btree block layout, cursor creation, staged commits, geometry/reservation calculations, cursor cache lifecycle, and in-memory rmap btree helpers.

## APIs And Macros

- `XFS_RMAP_BLOCK_LEN` defines the short-form CRC btree block header length.
- `XFS_RMAP_REC_ADDR`, `XFS_RMAP_KEY_ADDR`, `XFS_RMAP_HIGH_KEY_ADDR`, and `XFS_RMAP_PTR_ADDR` compute record, low-key, high-key, and pointer addresses.
- Declares `xfs_rmapbt_init_cursor`, `xfs_rmapbt_commit_staged_btree`, max-record/max-level functions, size/reserve functions, and cursor cache lifecycle.
- Declares `xfs_rmapbt_mem_cursor` and `xfs_rmapbt_mem_init` for in-memory reverse-map btrees.

## Dependencies

- Forward-declares buffers, cursors, mounts, staged btree fake roots, in-memory btree objects, transactions, perag structures, buftargs, and AG numbers through included type context.

## Invariants And Risks

- Rmap internal nodes store both low and high keys for each pointer; address macros reflect that doubled key area.
- Rmap btrees require CRC-enabled filesystem formats.
- In-memory cursor declarations are available from the header but implementation is conditional in the C file.
