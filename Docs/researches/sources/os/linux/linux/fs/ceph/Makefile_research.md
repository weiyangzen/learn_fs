# File Research: sources/os/linux/linux/fs/ceph/Makefile

## Purpose
Defines the CephFS client composite object list for the kernel build.

## Main Elements
- Core module target: `obj-$(CONFIG_CEPH_FS) += ceph.o`.
- Core sources: superblock, inode, directory, file, locks, address-space, ioctl, export, capabilities, snapshots, xattrs, quota, I/O, MDS client/map, strings, fragments, debugfs, utilities, and metrics.
- Optional sources: `cache.o` for `CONFIG_CEPH_FSCACHE`, `acl.o` for `CONFIG_CEPH_FS_POSIX_ACL`, and `crypto.o` for `CONFIG_FS_ENCRYPTION`.

## Dependencies And Integration
Maps Kconfig options to the CephFS build. The `acl.c` file in this group is built only when POSIX ACL support is enabled.

## Risk Notes
Optional files must match feature guards in headers and runtime code, particularly ACL, FS-Cache, and encryption integration points.
