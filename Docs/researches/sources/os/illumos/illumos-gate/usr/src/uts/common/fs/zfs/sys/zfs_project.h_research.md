# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_project.h

Defines ZFS project-id and project-inheritance ioctl compatibility types/constants.

Key elements:
- Maps `ZFS_PROJINHERIT_FL` to `FS_PROJINHERIT_FL` when available, otherwise uses `0x20000000`.
- Uses native `struct fsxattr` and `FS_IOC_FSGETXATTR`/`FS_IOC_FSSETXATTR` when present.
- Otherwise defines fallback `zfsxattr_t` with `fsx_xflags` and `fsx_projid`, plus illumos ioctl numbers.
- Defines `ZFS_DEFAULT_PROJID` as 0 and `ZFS_INVALID_PROJID` as all-ones.
- `zpl_is_valid_projid()` rejects the 32-bit projection of `ZFS_INVALID_PROJID`.

Main dependencies and interactions:
- Used by znode flags/project ID handling and project quota code.
- Has userland include hack to avoid pulling `sys/mount.h`.

Implementation notes:
- The inline validity check handles the mismatch between 32-bit ioctl project IDs and 64-bit internal invalid sentinel.
