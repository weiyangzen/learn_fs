# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_sb.h

## Purpose

`xfs_sb.h` declares the public libxfs superblock helper APIs used by mount, logging, geometry reporting, validation, and secondary superblock code.

## Main Content

- Declares superblock logging and syncing:
  - `xfs_log_sb`.
  - `xfs_sync_sb`.
  - `xfs_sync_sb_buf`.
- Declares mount-time common geometry setup and realtime extent-size update helpers.
- Declares superblock disk/in-core conversion and quota conversion helpers.
- Declares version/feature validation helpers.
- Declares secondary superblock update/read/get helpers.
- Defines maximum filesystem geometry ABI structure version as 5.
- Declares filesystem geometry fill helper.
- Declares stripe and realtime geometry validators.
- Declares realtime extent log and realtime group block log calculators.

## Key Interfaces and Invariants

- `xfs_sync_sb_buf` can update realtime superblocks via its `update_rtsb` argument.
- `xfs_fs_geometry` is versioned; callers provide the requested ABI structure version.
- Stripe geometry validation accepts a `may_repair` mode for mount-option overrides.

## Dependencies

Forward-declares XFS mount, superblock, disk superblock, transaction, geometry, and per-AG types. It relies on scalar XFS block/extent types from shared type headers.
