# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/uberblock.c

Implements basic uberblock verification and update logic.

Key elements:
- `uberblock_verify()` byteswaps the whole uberblock if the magic matches byteswapped `UBERBLOCK_MAGIC`, then validates the magic.
- `uberblock_update()` asserts txg monotonicity, fills magic, txg, root vdev guid sum, timestamp, software version, MMP magic/config fields, clears checkpoint txg, and reports whether the root block was born in this txg.

Main dependencies and interactions:
- Includes ZFS context, uberblock internals, vdev internals, and MMP.
- Reads root vdev `vdev_guid_sum` and pool multihost setting.
- Uses `zfs_multihost_interval` and `zfs_multihost_fail_intervals` for MMP config.

Implementation notes:
- It intentionally does not update `ub_version`, preserving older uberblock version behavior.
- MMP fields are zeroed when multihost is disabled.
