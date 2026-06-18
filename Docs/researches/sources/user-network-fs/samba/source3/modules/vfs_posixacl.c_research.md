# sources/user-network-fs/samba/source3/modules/vfs_posixacl.c

## Purpose
`vfs_posixacl.c` maps Samba's internal POSIX ACL representation to the platform POSIX ACL API. It implements fd/pathref ACL get, set, and default ACL delete hooks for systems exposing `acl_get_fd`, `acl_get_file`, `acl_set_fd`, `acl_set_file`, and `acl_delete_def_file`.

## Important APIs, Types, And Functions
- Public hooks: `posixacl_sys_acl_get_fd`, `posixacl_sys_acl_set_fd`, and `posixacl_sys_acl_delete_def_fd`.
- Conversion helpers: `smb_ace_to_internal`, `smb_acl_to_internal`, `smb_acl_set_mode`, and `smb_acl_to_posix`.
- Uses Samba types `SMB_ACL_T`, `SMB_ACL_TYPE_T`, `struct smb_acl_t`, and `struct smb_acl_entry`.
- `posixacl_fns` also wires `.sys_acl_blob_get_fd_fn = posix_sys_acl_blob_get_fd`.

## Control Flow
Get maps Samba ACL type to `ACL_TYPE_ACCESS` or `ACL_TYPE_DEFAULT`, chooses fd-based access ACL retrieval when possible, uses `/proc/fd` path support for pathrefs, or falls back to filename-based ACL calls. Retrieved platform ACL entries are iterated and converted into Samba entries. Set converts Samba entries into a platform ACL, validates it with `acl_valid`, and writes via fd, proc-fd path, or pathname. Default ACL delete uses proc-fd if available and pathname otherwise.

## State And Persistence
The module stores no private state. ACL state persists in the filesystem's ACL metadata. Temporary ACL objects are freed with `acl_free`; Samba ACL arrays are allocated on the caller's `TALLOC_CTX`.

## Dependencies And Integration Points
It depends on system POSIX ACL headers/APIs and Samba's ACL abstractions. It is a VFS module named `posixacl` and can be stacked where Samba needs direct POSIX ACL pass-through. It recognizes platform-specific `HAVE_ACL_GET_PERM_NP` and explicitly rejects `ACL_EVERYONE` with guidance to use `zfsacl`.

## Risks
- Pathname fallback is no longer truly handle-based and can be vulnerable to races compared with fd/proc-fd paths.
- Unsupported ACL tags fail conversion; FreeBSD/ZFS `ACL_EVERYONE` is intentionally not handled.
- ACL qualifier ownership and permission bit mapping must be exact to avoid access-control changes.
- `acl_valid` failures are logged with textual ACL output and must prevent invalid ACL persistence.

## Test Signals
- Round-trip user, group, owner, group object, mask, and other ACL entries through SMB and compare with native `getfacl`.
- Exercise pathref handles with and without proc-fd support.
- Attempt invalid Samba ACLs and verify `acl_valid` failure prevents write.
- Test default ACL deletion on directories.
