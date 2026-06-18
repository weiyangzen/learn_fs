# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/raidioctl.h

## Role

`raidioctl.h` defines ioctl numbers and structures for RAID controller configuration and firmware update operations.

## Ioctls and Status

The ioctl base is `RAID_IOC`, with commands:
- `RAID_GETCONFIG`: retrieve RAID volume information.
- `RAID_UPDATEFW`: update IOC firmware.
- `RAID_NUMVOLUMES`: retrieve maximum RAID volume count.

RAID flags include enabled, quiesced, and resyncing. RAID states are optimal, degraded, and failed. Disk status values are good, failed, and missing.

## Structures

`raid_config_t` reports:
- target/unit IDs.
- state/flags.
- RAID level.
- disk count, disk IDs, disk statuses.
- RAID capacity.

`RAID_MAXDISKS` is 32.

`update_flash_t` carries a firmware buffer pointer, size, and type. A 32-bit ABI variant `update_flash_32_t` is defined under `_SYSCALL32`.

## Research Notes

This is a small storage-management ABI. The fixed array sizes and 32-bit pointer translation are the main compatibility constraints.
