# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_fsmap.h

## Purpose

Defines internal GETFSMAP representations and declares the ioctl entry point.

## Main Types

- `struct xfs_fsmap`
  - device
  - flags
  - physical address
  - owner
  - owner offset
  - length
- `struct xfs_fsmap_head`
  - input flags
  - output flags
  - requested/returned entry counts
  - low/high keys
- `struct xfs_fsmap_irec`
  - internal record with start daddr, length, owner, offset, rmap flags, and source rmap key

## Main API

- `xfs_ioc_getfsmap`

## Research Notes

The header separates the userspace `fsmap` ABI from XFS’s internal block-unit and rmap-oriented representation.
