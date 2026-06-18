# File Research: sources/os/linux/linux/fs/sysfs/Makefile

Purpose: Builds the sysfs core object set.

Build contents:
- `obj-y := file.o dir.o symlink.o mount.o group.o`

Notes:
- sysfs is built as core kernel object code when enabled, not as a standalone module in this Makefile.
