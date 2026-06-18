# sources/user-network-fs/samba/source3/include/sysquotas.h

## Purpose
`sysquotas.h` defines source3 disk-quota constants, platform quota block-size selection, and the `SMB_DISK_QUOTA` structure used by VFS quota operations.

## Important APIs, Types, and Macros
- Platform includes under `HAVE_SYS_QUOTAS`: `mntent.h` when mount-entry helpers are available, or `devnm.h` on systems with `devnm`.
- Limit markers: `SMB_QUOTAS_NO_LIMIT` and `SMB_QUOTAS_NO_SPACE`.
- Initializer macros: `SMB_QUOTAS_SET_NO_LIMIT(dp)` and `SMB_QUOTAS_SET_NO_SPACE(dp)`.
- Main type: `SMB_DISK_QUOTA` holds quota type, block size, hard/soft block limits, current blocks, inode limits/current inodes, and flags.
- `QUOTABLOCK_SIZE` selection handles AIX, Linux, Darwin, BSD, and a fallback.

## Control Flow and State
The header's logic is compile-time platform selection. Runtime quota state is represented in `SMB_DISK_QUOTA` and filled by system/VFS quota functions.

## Persistence Behavior
No direct persistence. The VFS/system quota implementations that use `SMB_DISK_QUOTA` read or modify filesystem quota state.

## Dependencies and Integration Points
It depends on `enum SMB_QUOTA_TYPE` from surrounding includes and is included by `smb.h` and `vfs.h`. `SMB_DISK_QUOTA` is the argument type for `get_quota`/`set_quota` VFS function pointers and call wrappers.

## Risks
- Block-size mismatches can misreport or incorrectly set quota limits.
- The no-limit/no-space sentinel values are small integers in `uint64_t`; callers must not confuse them with real limits without context.
- Platform guards must match configure feature detection.

## Test Signals
Quota get/set tests on supported filesystems, build coverage on quota-enabled and quota-disabled platforms, unit checks for block-size conversion, and VFS quota module tests.
