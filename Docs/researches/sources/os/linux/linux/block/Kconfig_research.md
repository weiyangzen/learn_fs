# File Research: sources/os/linux/linux/block/Kconfig

This Kconfig file defines the core Linux block-layer configuration surface. `menuconfig BLOCK` enables the block layer, selects `FS_IOMAP` and `SBITMAP`, and gates all block-layer features in this file. Disabling it removes block device usability and disables storage stacks that rely on block-layer definitions.

Key options:
- `BLOCK_LEGACY_AUTOLOAD`: deprecated legacy module/device autoloading through device-node access.
- `BLK_DEV_INTEGRITY`: enables block data-integrity hooks and selects `CRC_T10DIF` and `CRC64`.
- `BLK_DEV_WRITE_MOUNTED`: controls whether mounted block devices may be written directly, with boot override `bdev_allow_write_mounted=`.
- `BLK_DEV_ZONED`: enables ZAC/ZBC/ZNS zoned block device support.
- `BLK_DEV_THROTTLING`, `BLK_CGROUP_IOLATENCY`, `BLK_CGROUP_IOCOST`, `BLK_CGROUP_IOPRIO`, `BLK_CGROUP_FC_APPID`: cgroup-based I/O policy and accounting features.
- `BLK_WBT` and `BLK_WBT_MQ`: writeback throttling and default enablement for request-based devices.
- `BLK_DEBUG_FS`: debugfs block-layer state.
- `BLK_SED_OPAL`: Opal self-encrypting drive support.
- `BLK_INLINE_ENCRYPTION` and fallback: blk-crypto and kernel crypto fallback.
- `BLK_PM`, `BLOCK_HOLDER_DEPRECATED`, `BLK_MQ_STACKING`: internal support switches.

It also includes `block/partitions/Kconfig` and `block/Kconfig.iosched`, so partition support and I/O scheduler choices are configured below this block-layer gate.
