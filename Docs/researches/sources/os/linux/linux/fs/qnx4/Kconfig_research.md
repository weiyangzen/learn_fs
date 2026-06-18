# File Research: sources/os/linux/linux/fs/qnx4/Kconfig

## Role

Kconfig option for QNX4 filesystem support.

## Contents

- `QNX4FS_FS`: tristate read-only QNX4 filesystem driver.
- Depends on `BLOCK`.
- Selects `BUFFER_HEAD`.
- Help text notes use for QNX 4 and QNX 6/QNX RTP disks, module name `qnx4`, and recommends `N` unless needed.

## Research Notes

Although the help mentions QNX6-era systems, this driver itself implements the older QNX4 on-disk format and is read-only.
