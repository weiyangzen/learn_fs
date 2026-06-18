# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_exchrange.h

## Purpose

Declares the internal data structure and APIs for XFS exchange-range and commit-range handling.

## Main Contents

- Private exchange flags:
  - `__XFS_EXCHANGE_RANGE_UPD_CMTIME1`
  - `__XFS_EXCHANGE_RANGE_UPD_CMTIME2`
  - `__XFS_EXCHANGE_RANGE_CHECK_FRESH2`
- `XFS_EXCHANGE_RANGE_PRIV_FLAGS`, grouping internal-only flag bits.
- `struct xfs_exchrange`, which stores:
  - two file pointers
  - offsets and length
  - public and private flags
  - file2 inode/generation/timestamp snapshot for freshness checks
- ioctl declarations:
  - `xfs_ioc_exchange_range`
  - `xfs_ioc_start_commit`
  - `xfs_ioc_commit_range`
- exchange-map locking and estimation helpers:
  - `xfs_exchrange_ilock`
  - `xfs_exchrange_iunlock`
  - `xfs_exchrange_estimate`

## Research Notes

This header is intentionally small. It separates the ioctl/file-level exchange contract from the lower exchange-map implementation while exposing only the helper routines needed by related XFS code.
