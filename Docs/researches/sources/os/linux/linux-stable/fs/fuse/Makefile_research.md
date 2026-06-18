# File Research: sources/os/linux/linux-stable/fs/fuse/Makefile

## Purpose
Builds the FUSE kernel objects and conditionally includes optional feature modules.

## Build Composition
- `obj-$(CONFIG_FUSE_FS) += fuse.o`
- `obj-$(CONFIG_CUSE) += cuse.o`
- `obj-$(CONFIG_VIRTIO_FS) += virtiofs.o`
- `fuse-y` starts with `trace.o` so ftrace errors surface early.
- Core FUSE objects include device, directory, file, inode, control, xattr, ACL, readdir, ioctl, and iomode support.
- Conditional objects:
  - `dax.o` for `CONFIG_FUSE_DAX`
  - `passthrough.o backing.o` for `CONFIG_FUSE_PASSTHROUGH`
  - `sysctl.o` for `CONFIG_SYSCTL`
  - `dev_uring.o` for `CONFIG_FUSE_IO_URING`
- `virtiofs-y := virtio_fs.o`

## Design Notes
The file keeps the main FUSE module as a composite object while CUSE and virtiofs are separate module targets.

## Dependencies
Uses kernel kbuild conventions and adds `ccflags-y = -I$(src)` for trace event headers.

## Research Notes
The grouped files map directly to these feature gates: ACL is always part of FUSE, backing is passthrough-only, DAX is DAX-only, and dev_uring is io_uring-only.
