# File Research: sources/os/linux/linux-stable/fs/proc/devices.c

## Purpose

Implements `/proc/devices`, listing registered character and, when enabled, block device majors.

## Main Responsibilities

- `devinfo_show()` prints:
  - `Character devices:` header at index zero.
  - Character device major entries through `chrdev_show()`.
  - Under `CONFIG_BLOCK`, `Block devices:` header and block majors through `blkdev_show()`.
- Provides seq iteration over major-number space:
  - `devinfo_start()`, `devinfo_next()`, and `devinfo_stop()`.
- `proc_devices_init()` creates a permanent `devices` seq entry.

## Notes

Iteration spans `CHRDEV_MAJOR_MAX + BLKDEV_MAJOR_MAX`; block output is conditionally compiled.
