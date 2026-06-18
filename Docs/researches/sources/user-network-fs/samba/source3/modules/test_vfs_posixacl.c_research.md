<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/test_vfs_posixacl.c -->
# sources/user-network-fs/samba/source3/modules/test_vfs_posixacl.c

## Purpose
This cmocka test verifies conversion from Samba's abstract POSIX ACL representation to a native POSIX `acl_t` in the `vfs_posixacl` module. It focuses on a simple ACL containing owner, group, and other entries.

## Important APIs, Types, And Functions
The file includes `vfs_posixacl.c` directly. `smb_acl_add_entry` constructs Samba ACL entries using `sys_acl_create_entry`, `sys_acl_set_tag_type`, optional `sys_acl_set_qualifier`, `sys_acl_get_permset`, `sys_acl_add_perm`, and `sys_acl_set_permset`. `acl_check_entry` inspects native entries with `acl_get_permset`, `acl_get_tag_type`, optional `acl_get_qualifier`, and `acl_get_perm` or `acl_get_perm_np`. `test_smb_acl_to_posix_simple_acl` calls `smb_acl_to_posix`.

## Control Flow
`main` requires an `smb.conf`, initializes talloc/loadparm state, and runs the single cmocka case. The case builds an SMB ACL with `SMB_ACL_USER_OBJ`, `SMB_ACL_GROUP_OBJ`, and `SMB_ACL_OTHER`, converts it, then iterates native ACL entries in order and checks tag and read/write/execute permissions.

## State And Persistence
All ACL structures are memory-local; the native ACL object is freed with `acl_free`, and the talloc frame is released. No filesystem ACLs are read or written.

## Dependencies And Integration Points
The test depends on POSIX ACL library functions, Samba's `sys_acl_*` compatibility layer, talloc, loadparm, and cmocka. It directly validates the utility path used when Samba converts internal ACL objects before calling platform ACL setters.

## Risks
Coverage is narrow: it does not test named users/groups, masks, default ACLs, deny-like cases, invalid ACLs, or filesystem set/get integration. Ordering expectations can be platform-sensitive if `smb_acl_to_posix` changes construction order.

## Test Signals
The strongest signal is successful conversion and native inspection of the three base ACL entries. Failing assertions point to tag mapping, qualifier handling, or permission-bit conversion bugs in `vfs_posixacl.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/test_vfs_posixacl.c -->
