# File Research: sources/os/linux/linux/fs/ceph/Kconfig

## Purpose
Defines build-time configuration for the Linux CephFS client and optional CephFS features.

## Main Elements
- `CEPH_FS`: tristate Ceph distributed filesystem client, depending on `INET`, selecting `CEPH_LIB`, `NETFS_SUPPORT`, and encryption algorithms when fs encryption is enabled.
- `CEPH_FSCACHE`: optional persistent read-only local caching support through FS-Cache, constrained by whether CephFS and FS-Cache are built-in or modular.
- `CEPH_FS_POSIX_ACL`: optional POSIX ACL support, selecting `FS_POSIX_ACL`.
- `CEPH_FS_SECURITY_LABEL`: optional security label xattr support when Linux security modules are enabled.

## Dependencies And Integration
Controls which CephFS source files are built in `fs/ceph/Makefile` and connects CephFS to netfs, FS-Cache, encryption, POSIX ACL, and LSM infrastructure.

## Risk Notes
The FS-Cache dependency expression preserves module/built-in compatibility. ACL and security-label support are separate feature gates, so builds can include CephFS without those xattr-related paths.
