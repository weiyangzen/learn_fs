# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr_remote.h

## Purpose
Declares the remote extended attribute value helper API used by attr leaf and delayed attr operation code.

## Main Interfaces
- `xfs_attr3_rmt_blocks()` computes the number of attr-fork blocks required for a value.
- `xfs_attr3_max_rmt_blocks()` returns the block count for `XFS_XATTR_SIZE_MAX`.
- `xfs_attr_rmtval_get()` reads a remote value.
- `xfs_attr_rmtval_stale()` marks cached remote value buffers stale.
- `xfs_attr_rmtval_invalidate()` invalidates remote buffers before removal.
- `xfs_attr_rmtval_remove()` unmaps remote value blocks.
- `xfs_attr_rmt_find_hole()`, `xfs_attr_rmtval_find_space()`, `xfs_attr_rmtval_set_blk()`, and `xfs_attr_rmtval_set_value()` support delayed allocation and writing of remote values.

## Integration Points
Included by `xfs_attr.c`, `xfs_attr_leaf.c`, and `xfs_attr_remote.c`. The prototypes connect leaf entries that reference remote values to bmap allocation/removal and synchronous remote buffer IO.

## Risks And Review Focus
- Block-count helpers must remain in lockstep with CRC header sizing in `xfs_attr_remote.c`.
- Delayed operation helpers depend on `struct xfs_attr_intent` state fields declared in `xfs_attr.h`.
