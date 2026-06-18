# File Research: sources/os/linux/linux-stable/fs/ceph/Kconfig

This Kconfig file defines CephFS client filesystem build options.

Configuration entries:
- `CEPH_FS`: tristate Ceph distributed filesystem client. It depends on `INET`, selects `CEPH_LIB`, `NETFS_SUPPORT`, and `FS_ENCRYPTION_ALGS` when filesystem encryption is enabled. It defaults to `n`.
- `CEPH_FSCACHE`: optional persistent read-only local caching support using FS-Cache. It is available only when CephFS and FS-Cache linkage are compatible: module CephFS with FS-Cache or built-in CephFS with built-in FS-Cache.
- `CEPH_FS_POSIX_ACL`: optional POSIX ACL support. It depends on `CEPH_FS` and selects `FS_POSIX_ACL`.
- `CEPH_FS_SECURITY_LABEL`: optional security label xattr support. It depends on `CEPH_FS` and `SECURITY`.

This file places CephFS in the same netfs ecosystem as CacheFiles by selecting `NETFS_SUPPORT` and optionally using FS-Cache. The ACL option controls compilation of `acl.o` from the Makefile.
