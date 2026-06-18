# File Research: sources/os/linux/linux/fs/proc/devices.c

## Purpose
Implements `/proc/devices`, listing registered character and block device majors.

## Main Responsibilities
- Iterates through character major range and, when block support is enabled, block major range.
- Emits section headers for character and block devices.
- Calls `chrdev_show()` and `blkdev_show()` for per-major content.
- Registers a permanent seq proc entry named `devices`.

## Key Interfaces
- `devinfo_show()`
- `devinfo_ops`
- `proc_devices_init()`

## Dependencies and Integration
Depends on character device registry, optional block device registry, seq_file, and procfs.

## Risks and Review Hotspots
- Iteration bounds combine `CHRDEV_MAJOR_MAX` and `BLKDEV_MAJOR_MAX`; block-disabled builds still compile with the shared logic.
- Output format is longstanding userspace ABI for device discovery/debugging.
