# File Research: sources/os/linux/linux-stable/fs/fuse/Kconfig

## Purpose
Defines kernel configuration options for FUSE, CUSE, virtiofs, DAX, passthrough, and io_uring-based FUSE communication.

## Options
- `FUSE_FS`: main Filesystem in Userspace support; selects POSIX ACL and iomap support.
- `CUSE`: character devices in userspace; depends on `FUSE_FS`.
- `VIRTIO_FS`: host/guest filesystem sharing over virtio; depends on `FUSE_FS` and selects `VIRTIO`.
- `FUSE_DAX`: direct host memory access for virtiofs; depends on virtiofs, FS_DAX, and DAX; selects interval trees.
- `FUSE_PASSTHROUGH`: maps selected FUSE operations to backing files; selects `FS_STACK`.
- `FUSE_IO_URING`: enables FUSE request transport through io_uring; depends on `FUSE_FS` and `IO_URING`.

## Design Notes
The default-enabled booleans for DAX, passthrough, and io_uring expose optional acceleration paths when their dependencies are present.

## Dependencies
References documentation under `Documentation/filesystems/fuse/fuse.rst` and depends on broader VFS, virtio, DAX, and io_uring subsystems.

## Research Notes
This file establishes which companion objects in the FUSE Makefile participate in the build.
