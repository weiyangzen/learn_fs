# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_fork.h

## Role
`xfs_inode_fork.h` defines the in-core inode fork structure and declares APIs for fork import, flush, destruction, extent tree manipulation, local data management, and extent count limit handling.

## Main Definitions
- `struct xfs_ifork` stores fork data bytes, in-core btree root, modification sequence, extent-tree height, data/root pointer, extent count, btree root byte size, fork format, and deferred extent-read flag.
- `XFS_IEXT_*_CNT` macros estimate worst-case extent count growth for operations such as adds, hole punches, attr manipulation, unwritten conversion, reflink CoW completion, and rmap swaps.
- `XFS_IFORK_MAXEXT` computes how many bmbt records fit in a fork region.
- `xfs_iext_max_nextents` returns small or large extent-count limits for data/CoW versus attr forks.
- `xfs_dfork_*_extents` helpers read small or large dinode extent counters.

## Exported API
- Fork initialization/import/flush: `xfs_iformat_data_fork`, `xfs_iformat_attr_fork`, `xfs_ifork_init_attr`, `xfs_ifork_zap_attr`, `xfs_iflush_fork`, and `xfs_ifork_init_cow`.
- Memory lifecycle: `xfs_idestroy_fork`, `xfs_idata_realloc`, `xfs_broot_alloc`, `xfs_broot_realloc`, and `xfs_init_local_fork`.
- Extent tree operations: insert, remove, lookup, lookup-before, get, update, cursor movement, peek helpers, and `for_each_xfs_iext`.
- Extent loading/copying: `xfs_iread_extents`, `xfs_iextents_copy`, and `xfs_need_iread_extents`.
- Validation and policy: `xfs_ifork_verify_local_data`, `xfs_ifork_verify_local_attr`, `xfs_iext_count_extend`, and `xfs_ifork_is_realtime`.

## Data and Invariants
- A null fork pointer is treated as empty extents format by `xfs_ifork_nextents` and `xfs_ifork_format`.
- Forks have extents only when format is `EXTENTS` or `BTREE`.
- `xfs_need_iread_extents` uses acquire semantics paired with import-time release stores.
- Cursor helpers expose a stable iteration idiom without exposing the extent tree layout.

## Dependencies
The header connects inode fork users to bmap state, dinode formats, transaction logging, and in-core extent tree operations.

## Research Notes
This header is the public map for inode fork storage. It encodes both representation details (`struct xfs_ifork`) and operation-risk estimates used before metadata updates grow extent counts.
