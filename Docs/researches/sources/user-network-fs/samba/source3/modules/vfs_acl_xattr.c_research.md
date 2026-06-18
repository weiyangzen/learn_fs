<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_acl_xattr.c -->
# sources/user-network-fs/samba/source3/modules/vfs_acl_xattr.c

## Purpose
This VFS module stores Windows NT ACL blobs in file extended attributes. It is the xattr backend for `vfs_acl_common.c` and also hides or remaps a configured security ACL xattr name from normal client xattr operations.

## Important APIs, Types, And Functions
The module registers as `acl_xattr`. Backend helpers are `getxattr_do`, `fget_acl_blob`, `store_acl_blob_fsp`, and `sys_acl_set_fd_xattr`. VFS entry points include `connect_acl_xattr`, `acl_xattr_unlinkat`, `acl_xattr_fget_nt_acl`, `acl_xattr_fset_nt_acl`, async `acl_xattr_getxattrat_send/recv`, and fget/flist/fremove/fset xattr wrappers that protect or remap configured ACL xattr names.

## Control Flow
Connect initializes common config, forces Windows ACL-friendly share parameters, optionally adjusts masks and DOS attribute settings for `ignore system acls`, and reads `acl_xattr:security_acl_name`. ACL get reads `XATTR_NTACL_NAME` as root with a retry loop for `ERANGE` up to 65536 bytes, then delegates validation to common code. ACL set delegates descriptor merging and storage to common code, and storage writes the xattr as root. POSIX ACL changes remove the NTACL xattr unless guarded by an in-progress NT ACL set. Client xattr operations deny direct access to the configured hidden security xattr and optionally translate public `XATTR_NTACL_NAME` to the configured private name.

## State And Persistence
NT ACLs are persisted per file in `XATTR_NTACL_NAME` or a configured security ACL xattr name. Per-handle config stores xattr-name policy. There is no module-global database state.

## Dependencies And Integration Points
Dependencies include Samba VFS xattr operations, common ACL helpers, tevent async wrappers, loadparm, auth/root privilege helpers, and NTSTATUS/Unix error mapping. The module is stackable and forwards unlink/chmod and xattr operations to the next VFS layer after applying ACL-specific policy.

## Risks
The xattr get loop must avoid unbounded allocation and currently caps at 64 KiB. Hidden xattr remapping is easy to misconfigure; direct access to the real security xattr is denied to prevent clients from bypassing ACL semantics. Set xattr and DOS/common ACL changes are not a single filesystem transaction. Filesystems without xattr support will return mapped Unix errors.

## Test Signals
Key tests include ACL get/set round trips, `ERANGE` resize, missing xattr fallback to filesystem ACLs, configured `security_acl_name` remapping, denial of direct private xattr access, list filtering, POSIX ACL set invalidating stored NTACLs, and async getxattrat behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_acl_xattr.c -->
