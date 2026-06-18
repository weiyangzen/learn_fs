# File Research: sources/os/linux/linux/block/partitions/mac.h

## Summary
Defines Apple Partition Map constants and packed-ish on-disk structures used by `mac.c`.

## Main Contents
- `MAC_PARTITION_MAGIC`, `MAC_DRIVER_MAGIC`, and `MAC_STATUS_BOOTABLE`.
- `APPLE_AUX_TYPE`.
- `struct mac_partition`.
- `struct mac_driver_desc`.

## Important Details
`mac_partition` stores big-endian map count, start block, block count, status, boot fields, and fixed-size name/type/processor strings. `mac_driver_desc` provides the block size needed to locate partition-map entries.

## Risks
Fields are big-endian and represent Apple block units, not Linux 512-byte sectors. Consumers must convert both endian and unit size.
