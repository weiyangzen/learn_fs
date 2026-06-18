# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_acl.c

## Scope

This file implements SMBFS ACL and security descriptor support for ioctl, `VOP_GETSECATTR`, `VOP_SETSECATTR`, and owner/group attribute refresh.

## APIs And Behavior

- `smbfs_getsd()` obtains a security descriptor by temporary-opening the node with read-control and optional system-security rights, retrying with a larger buffer when the server reports more data.
- `smbfs_setsd()` temporary-opens with rights implied by owner/group/DACL/SACL selectors, invalidates the cached security attributes, and sends a remote set-security operation.
- `smbfs_acl_iocget()` handles `SMBFSIO_GETSD`, returning required/used buffer size and copying the raw descriptor to user memory.
- `smbfs_acl_iocset()` handles `SMBFSIO_SETSD`, validates descriptor size, copies user data into an mbchain, and sends it.
- `smbfs_acl_refresh()` fetches owner, group, and DACL information, parses the NT security descriptor, converts it to ZFS ACL form, and updates `r_secattr`, `n_uid`, and `n_gid`.
- `smbfs_acl_getids()` refreshes cached UID/GID when stale.
- `smbfs_acl_getvsa()` refreshes and duplicates requested ACL fields into caller-supplied `vsecattr_t`.
- `smbfs_acl_store()` converts ZFS ACL/UID/GID inputs to an NT security descriptor and sends it.
- `smbfs_acl_setids()` updates owner and/or group security fields.
- `smbfs_acl_setvsa()` sets DACL information using current owner/group for owner/group ACE expansion.

## State And Dependencies

- Depends on `smbfs_ntacl.h` conversion/marshalling helpers, mchain, temporary open/close helpers, and SMBFS SMB security operations.
- Uses `r_sectime` as ACL cache expiry and `r_statelock` for cached security fields.

## Risks And Invariants

- Raw security descriptors are bounded by `MAX_RAW_SD_SIZE` and `SMALL_SD_SIZE` retry logic.
- Extended attribute files/directories report `ENOSYS` because their ACLs are derived from parents.
- `smbfs_setsd()` consumes the passed mblk pointer and clears it.
- Old cached ACL allocations must be freed after replacement.
