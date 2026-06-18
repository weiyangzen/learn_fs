# File Research: sources/os/linux/linux/fs/qnx6/Kconfig

## Role

Kconfig options for QNX6 filesystem support.

## Contents

- `QNX6FS_FS`: tristate read-only QNX6 filesystem driver.
- Depends on `BLOCK && CRC32`.
- Selects `BUFFER_HEAD`.
- `QNX6FS_DEBUG`: optional extended debug output.

## Research Notes

The driver is explicitly read-only and uses CRC32 superblock validation.
