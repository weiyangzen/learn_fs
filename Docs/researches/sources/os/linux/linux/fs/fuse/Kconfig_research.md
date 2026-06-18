# File Research: sources/os/linux/linux/fs/fuse/Kconfig

## Purpose
This Kconfig file declares the build-time configuration options for FUSE, CUSE, virtiofs, virtiofs DAX, FUSE passthrough, and FUSE io_uring communication.

## Main Definitions
- `FUSE_FS`: tristate base support for Filesystem in Userspace; selects `FS_POSIX_ACL` and `FS_IOMAP`.
- `CUSE`: tristate Character device in Userspace support; depends on `FUSE_FS`.
- `VIRTIO_FS`: tristate virtio filesystem support; depends on `FUSE_FS` and selects `VIRTIO`.
- `FUSE_DAX`: bool virtiofs direct host memory access; default `y`; depends on `VIRTIO_FS`, `FS_DAX`, and `DAX`; selects `INTERVAL_TREE`.
- `FUSE_PASSTHROUGH`: bool passthrough operations; default `y`; depends on `FUSE_FS`; selects `FS_STACK`.
- `FUSE_IO_URING`: bool FUSE communication over io_uring; default `y`; depends on `FUSE_FS` and `IO_URING`.

## Behavior And Build Impact
The base `FUSE_FS` option enables the core userspace filesystem stack. CUSE and virtiofs are optional frontends/extensions. DAX, passthrough, and io_uring each conditionally include specialized implementation files through the Makefile.

## Dependencies And Interfaces
This file establishes compile-time feature gates used by `fs/fuse/Makefile` and by `#ifdef CONFIG_FUSE_*` sections in source files such as `dev.c`, `dax.c`, `backing.c`, and `dev_uring.c`.

## Research Notes
The default-enabled bool options mean that when their dependencies are present, DAX, passthrough, and io_uring support are included unless disabled by the kernel configuration.
