# File Research: sources/os/linux/linux-stable/fs/qnx4/Kconfig

## Summary
Kconfig option for read-only QNX4 filesystem support.

## Main Responsibilities
- Define `QNX4FS_FS` as a tristate filesystem option.
- Depend on block-device support.
- Select `BUFFER_HEAD`.
- Document that the module name is `qnx4`.

## Cross-File Interactions
Controls compilation of `fs/qnx4/Makefile` and the read-only QNX4 filesystem implementation.
