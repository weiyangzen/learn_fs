# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_missing.c

## Purpose
Defines placeholder vdev operations for `missing` and `hole` vdev types. A missing vdev is used during import to represent a known-absent device while still allowing the rest of the pool configuration to be parsed and opened.

## Main Behavior
- `vdev_missing_open()` pretends to succeed with zero physical size, max size, and ashift. This avoids the root vdev being marked `VDEV_AUX_NO_REPLICAS`; the pool should later fail the GUID-sum check with `VDEV_AUX_BAD_GUID_SUM`.
- `vdev_missing_close()` is a no-op.
- `vdev_missing_io_start()` fails any I/O with `ENOTSUP` and executes the zio completion path.
- `vdev_missing_io_done()` is a no-op.

## Registered Ops
- `vdev_missing_ops` uses type `VDEV_TYPE_MISSING`.
- `vdev_hole_ops` uses type `VDEV_TYPE_HOLE`.
- Both are leaf vdevs with default asize and no remap/xlate/dump handlers.

## Important Behavior And Invariants
The GUID for a missing vdev is always zero, so the root configuration's GUID sum will not match. This file intentionally supports import-time diagnosis rather than operational I/O.
