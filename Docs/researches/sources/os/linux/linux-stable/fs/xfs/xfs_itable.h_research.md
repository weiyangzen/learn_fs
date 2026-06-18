# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_itable.h

This header defines the in-memory bulk inode request structure and declares bulkstat/inumbers APIs.

Contents:
- `struct xfs_ibulk`:
  - Mount pointer.
  - Mount idmap.
  - Userspace output buffer.
  - Start inode cursor.
  - Input count and output count.
  - Bulk flags.
  - Iwalk flags.
- Flags:
  - `XFS_IBULK_NREXT64` requests 64-bit extent count output.
  - `XFS_IBULK_METADIR` allows metadata directory records.
- `xfs_ibulk_advance` advances the userspace buffer pointer, increments output count, and returns `-ECANCELED` when the requested count is filled.
- Formatter callback typedefs for bulkstat and inumbers.
- Function declarations for:
  - `xfs_bulkstat_one`
  - `xfs_bulkstat`
  - `xfs_bulkstat_to_bstat`
  - `xfs_inumbers`
  - `xfs_inumbers_to_inogrp`

Role:
- Provides the shared request/formatter abstraction used by native ioctl, compat ioctl, and itable implementation.
