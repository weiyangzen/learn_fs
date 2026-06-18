# File Research: sources/os/linux/linux-stable/fs/ceph/Makefile

This Makefile builds the Ceph filesystem client module.

Main target:
- `obj-$(CONFIG_CEPH_FS) += ceph.o`

Core CephFS objects:
- `super.o`, `inode.o`, `dir.o`, `file.o`, `locks.o`, `addr.o`, `ioctl.o`
- `export.o`, `caps.o`, `snap.o`, `xattr.o`, `quota.o`, `io.o`
- `mds_client.o`, `mdsmap.o`, `strings.o`, `ceph_frag.o`
- `debugfs.o`, `util.o`, `metric.o`, `subvolume_metrics.o`

Optional objects:
- `cache.o` when `CONFIG_CEPH_FSCACHE` is enabled.
- `acl.o` when `CONFIG_CEPH_FS_POSIX_ACL` is enabled.
- `crypto.o` when `CONFIG_FS_ENCRYPTION` is enabled.

The file shows CephFS as a multi-component network filesystem client with optional local caching, ACLs, and encryption support.
