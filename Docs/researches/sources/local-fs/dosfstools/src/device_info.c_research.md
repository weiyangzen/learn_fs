# File Research: sources/local-fs/dosfstools/src/device_info.c

Device discovery layer used by `mkfs.fat` and `testdevinfo`.

Main behavior:
- Initializes `struct device_info` with unknown/default sentinel values.
- `get_device_info()` classifies target file descriptor:
  - regular file: `TYPE_FILE`, partition 0, size from `st_size`
  - non-block non-file: `TYPE_BAD`
  - block device: gathers size, geometry, sector size, and Linux sysfs metadata.
- Linux-specific `get_block_linux_info()`:
  - Opens `/sys/dev/block/<major>:<minor>`.
  - Detects partition number from `partition`.
  - Reads whole-disk sector size from parent `../size`.
  - Detects children by scanning partition subdirectories and `holders`.
  - Detects virtual devices through `slaves`.
  - Detects loop devices backed by regular files via `LOOP_GET_STATUS64`.
  - Reads `removable` to classify fixed versus removable.
- `is_device_mounted()` checks mount tables through `getmntent()` or `getmntinfo()` depending on platform.

Dependencies:
- Uses `blkdev_get_size`, `blkdev_get_geometry`, `blkdev_get_start`, and `blkdev_get_sector_size`.
- Uses Linux `major`/`minor`, sysfs, and optional loop headers when available.

Research notes:
- This file intentionally separates mkfs safety heuristics from raw block-device ioctl helpers.
- `device_info_verbose` is declared but not used inside this file; likely consumed elsewhere.
