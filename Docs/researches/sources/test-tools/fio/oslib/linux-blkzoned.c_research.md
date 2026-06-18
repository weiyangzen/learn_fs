# sources/test-tools/fio/oslib/linux-blkzoned.c

Purpose: Linux implementation of fio's zoned block device abstraction.

Important APIs/functions: implements `blkzoned_get_zoned_model()`, `blkzoned_get_max_open_zones()`, `blkzoned_get_max_active_zones()`, `blkzoned_report_zones()`, `blkzoned_reset_wp()`, `blkzoned_finish_zone()`, and `blkzoned_move_zone_wp()`. Internal helpers read sysfs attributes and compute zone capacity.

Control flow: sysfs helpers resolve `/sys/dev/block/<major>:<minor>`, follow symlinks, strip partition components when needed, and read queue attributes. Zone reporting opens the block device, allocates a `blk_zone_report`, issues `BLKREPORTZONE`, and converts Linux sector units and zone types/conditions into fio `zbd_zone` fields. Reset/finish build `blk_zone_range` and issue `BLKRESETZONE` or `BLKFINISHZONE`, opening the file temporarily if fio has not already opened it. Write-pointer movement uses `fallocate(FALLOC_FL_ZERO_RANGE)` when no buffer is provided, otherwise `pwrite()`.

State and persistence: no module-global state. Operations can persistently change device write pointers or zone conditions. The code uses caller-owned `fio_file` state and closes only fds it opened itself.

Dependencies and integration: Linux block zoned UAPI, sysfs, fio `zbd_types`, `fio_file`, logging, `smalloc`/verification contexts, and `asprintf()`. It provides the `CONFIG_HAS_BLKZONED` backend declared in `blkzoned.h`.

Risks: requires block devices; non-block files return errors or no zoned model. Older UAPI headers are handled with local struct definitions, but kernel behavior still varies. `readlink()` path handling assumes sysfs canonical layout. `BLKFINISHZONE` treats `ENOTTY` as success for older kernels, which may hide unsupported behavior.

Test signals: ZBD integration tests on host-aware/host-managed devices, partition devices, old kernels lacking capacity or finish-zone support, and sysfs attribute absence.
