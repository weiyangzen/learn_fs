# File Research: sources/os/linux/linux/block/partitions/core.c

## Summary
Implements the Linux block partition scanning core. It orders partition-table probes, owns `parsed_partitions` allocation, creates/removes partition `block_device` instances, exposes partition sysfs attributes, and handles disk rescans.

## Main Responsibilities
- Defines the global partition probe order in `check_part[]`.
- Allocates and frees partition parse state and parse output buffers.
- Runs table recognizers until one succeeds.
- Adds, deletes, resizes, and drops partition devices.
- Handles `bdev_disk_changed()` rescans and media invalidation.
- Reads partition-table sectors through the whole-disk page cache.

## Key APIs
- `bdev_add_partition()`, `bdev_del_partition()`, `bdev_resize_partition()`.
- `bdev_disk_changed()`.
- `drop_partition()`.
- `read_part_sector()`.
- Internal helpers: `check_partition()`, `add_partition()`, `blk_add_partitions()`.

## Important Behavior
GPT is probed before MSDOS, and LDM is also probed before MSDOS so those table formats can claim disks before generic MBR parsing.

`add_partition()` creates a child block device, assigns either an in-range minor or an extended block minor, attaches metadata such as UUID/volume name, creates the `holders` kobject, and finally inserts it into `disk->part_tbl`.

Partition addition rejects host-managed zoned whole disks, duplicate partition numbers, and partitions beyond `DISK_MAX_PARTS`. Rescan paths remove existing partitions only while `open_mutex` is held and no partitions are open.

If a table or partition extends beyond end-of-device, the code can call `unlock_native_capacity()` once and retry scanning.

## State and Synchronization
Partition table mutation is serialized by `disk->open_mutex`. Partition lookup during overlap checks uses RCU over the disk xarray. Device lifetime is tied to block-device references, device refs, kobject refs, and `part_release()` cleanup.

## Risks
The probe order is behaviorally significant; moving recognizers can make stale or protective tables claim disks incorrectly. Rescan correctness depends on open counts, holder state, and xarray/device lifetime staying consistent.
