# sources/user-network-fs/samba/source3/modules/non_posix_acls.c

## Purpose
Builds a stable serialized hash wrapper for non-POSIX ACL blobs by combining the ACL blob with current file owner, group, and mode metadata.

## APIs, Types, And Control Flow
The exported helper `non_posix_sys_acl_blob_get_fd_helper()` takes an existing ACL `DATA_BLOB`, obtains file stat data from `fsp->fsp_name->st` or `smb_vfs_call_fstat`, fills `xattr_sys_acl_hash_wrapper` with ACL blob, uid, gid, and mode, and NDR-pushes that wrapper into the output blob. On stat failure it returns `-1`; on NDR failure it sets `errno = EINVAL`.

## State, Dependencies, Integration
The helper uses only stack/talloc-frame state. It persists nothing directly; callers use the output blob as an ACL identity/hash source. Dependencies are generated `ndr_xattr.h`, Samba VFS fstat, DATA_BLOB, and talloc. It integrates with VFS modules that expose ACL blobs but do not use POSIX ACL syscalls.

## Risks And Test Signals
Risk centers on metadata coupling: owner/group/mode changes alter the wrapper even when the ACL blob is unchanged. Tests should cover valid cached stat, fstat fallback, fstat failure, NDR serialization failure, and ensuring uid/gid/mode changes produce distinct output blobs.
