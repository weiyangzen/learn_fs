# File Research: sources/os/linux/linux/fs/xfs/xfs_exchrange.h

Declares the internal state and entry points for XFS range exchange and commit-range operations.

Key contents:
- Private high-bit flags:
  - `__XFS_EXCHANGE_RANGE_UPD_CMTIME1`
  - `__XFS_EXCHANGE_RANGE_UPD_CMTIME2`
  - `__XFS_EXCHANGE_RANGE_CHECK_FRESH2`
  - `XFS_EXCHANGE_RANGE_PRIV_FLAGS`
- `struct xfs_exchrange`, carrying file pointers, byte offsets, length, public/private flags, and the file2 freshness snapshot used by commit-range.
- Ioctl entry points: `xfs_ioc_exchange_range`, `xfs_ioc_start_commit`, `xfs_ioc_commit_range`.
- Shared inode locking helpers and exchange-map resource estimation declaration.

This header is the narrow interface between ioctl handling, generic exchange validation, and lower-level `xfs_exchmaps` work.
