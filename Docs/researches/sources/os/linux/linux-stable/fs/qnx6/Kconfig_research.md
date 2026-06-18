# File Research: sources/os/linux/linux-stable/fs/qnx6/Kconfig

## Summary
Kconfig options for read-only QNX6 filesystem support and optional debug logging.

## Main Responsibilities
- Define `QNX6FS_FS` as a tristate option depending on `BLOCK` and `CRC32`.
- Select `BUFFER_HEAD`.
- Document that the module is `qnx6` and currently read-only.
- Define `QNX6FS_DEBUG` to enable extended debug output.

## Cross-File Interactions
Controls the QNX6 object build and optionally adds `-DDEBUG` through the Makefile.
