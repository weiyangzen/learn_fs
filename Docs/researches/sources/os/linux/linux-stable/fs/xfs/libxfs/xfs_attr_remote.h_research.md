# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr_remote.h

## Purpose

`xfs_attr_remote.h` declares the remote extended attribute value helpers implemented by `xfs_attr_remote.c`. It is the interface used by attr leaf and state-machine code when a value is too large to store inline in a leaf entry.

## APIs

- `xfs_attr3_rmt_blocks` computes remote fsblocks required for a value.
- `xfs_attr3_max_rmt_blocks` returns the remote block count for the maximum xattr size.
- `xfs_attr_rmtval_get` reads a remote value into `args->value`.
- `xfs_attr_rmtval_stale` marks cached remote value buffers stale for a mapped extent.
- `xfs_attr_rmtval_invalidate` invalidates all remote buffers for an attr value before removal.
- `xfs_attr_rmtval_remove` unmaps remote value extents, potentially across transaction rolls.
- `xfs_attr_rmt_find_hole` finds unused attr fork space for a remote value.
- `xfs_attr_rmtval_set_value` synchronously writes the value into already allocated extents.
- `xfs_attr_rmtval_set_blk` allocates one remote extent step for a delayed intent.
- `xfs_attr_rmtval_find_space` initializes delayed remote allocation state.

## Integration Notes

The header assumes `struct xfs_mount`, `struct xfs_da_args`, `struct xfs_attr_intent`, `struct xfs_inode`, and `struct xfs_bmbt_irec` are visible through surrounding XFS headers. Callers must preserve the remote metadata fields in `xfs_da_args` across state-machine steps.
