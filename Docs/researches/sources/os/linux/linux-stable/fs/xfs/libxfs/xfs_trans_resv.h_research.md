# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_trans_resv.h

## Purpose

Defines transaction reservation structures, standard transaction log counts, directory operation reservation macros, and reservation calculation APIs.

## Main Types

- `struct xfs_trans_res`
  - per-ticket log bytes
  - log operation count
  - reservation flags
- `struct xfs_trans_resv`
  - named reservation slots for XFS transaction classes, including write, truncate, namespace operations, growfs, attributes, quota, superblock, and atomic ioend.

## Main Macros

- `M_RES(mp)` accesses mount transaction reservations.
- `XFS_DIROP_LOG_RES`
- `XFS_DIROP_LOG_COUNT`
- Standard log counts such as:
  - `XFS_WRITE_LOG_COUNT`
  - `XFS_ITRUNCATE_LOG_COUNT`
  - `XFS_CREATE_LOG_COUNT`
  - `XFS_RENAME_LOG_COUNT`
  - `XFS_ATTRSET_LOG_COUNT`
- Historical reflink log counts retained for minimum log sizing.

## Main API

- `xfs_trans_resv_calc`
- Deferred completion reservation calculators:
  - BUI
  - EFI and realtime EFI
  - RUI and realtime RUI
  - CUI and realtime CUI
- Minimum-log-size reservation calculators.
- Atomic write reservation calculators.

## Research Notes

This header is the public interface for the reservation engine implemented in `xfs_trans_resv.c`.
