# File Research: sources/os/linux/linux/fs/fuse/Makefile

## Purpose
This Makefile describes how the FUSE-related kernel objects are built and linked.

## Main Definitions
- Adds `-I$(src)` to `ccflags-y` for trace event include resolution.
- Builds `fuse.o` when `CONFIG_FUSE_FS` is enabled.
- Builds `cuse.o` when `CONFIG_CUSE` is enabled.
- Builds `virtiofs.o` when `CONFIG_VIRTIO_FS` is enabled.
- Places `trace.o` first in `fuse-y` so ftrace-related errors surface early.
- Core `fuse-y` includes `dev.o`, `dir.o`, `file.o`, `inode.o`, `control.o`, `xattr.o`, `acl.o`, `readdir.o`, `ioctl.o`, and `iomode.o`.
- Conditional objects include `dax.o`, `passthrough.o`, `backing.o`, `sysctl.o`, and `dev_uring.o`.
- `virtiofs-y` maps to `virtio_fs.o`.

## Research Notes
The build layout mirrors the Kconfig feature boundaries. The files in this batch cover several core and conditional objects: `dev.o`, `control.o`, `acl.o`, `backing.o`, `dax.o`, `dev_uring.o`, and `cuse.o`.
