# sources/user-network-fs/samba/source3/include/smb_acls.h

## Purpose
`smb_acls.h` defines Samba's portable POSIX ACL abstraction for source3. It maps Samba ACL handles, entries, permission sets, and tags onto generated NDR ACL types and declares the `sys_acl_*` helper API implemented by `lib/sysacls.c`.

## Important APIs, Types, and Functions
- Type aliases: `SMB_ACL_TYPE_T`, `SMB_ACL_PERMSET_T`, `SMB_ACL_PERM_T`, `SMB_ACL_TAG_T`, `SMB_ACL_T`, and `SMB_ACL_ENTRY_T`.
- ACL traversal/query: `sys_acl_get_entry`, `sys_acl_get_tag_type`, `sys_acl_get_permset`, `sys_acl_get_qualifier`, `sys_acl_get_perm`, and `sys_acl_to_text`.
- ACL construction/mutation: `sys_acl_init`, `sys_acl_create_entry`, `sys_acl_set_tag_type`, `sys_acl_set_qualifier`, `sys_acl_set_permset`, `sys_acl_clear_perms`, and `sys_acl_add_perm`.
- File-handle operations: `sys_acl_get_fd`, `sys_acl_set_fd`, and `sys_acl_delete_def_fd`.
- Error classification: `no_acl_syscall_error`.

## Control Flow and State
The header is an interface only. Runtime control flow is the standard Samba ACL path: VFS ACL calls dispatch to system ACL helpers, which create/read/modify `SMB_ACL_T` structures and convert them to or from SMB security descriptors. ACL state lives in the allocated ACL object and on the backing filesystem ACLs associated with `files_struct` handles.

## Persistence Behavior
Persistence is through the host filesystem's ACL mechanism via file-descriptor operations. The header itself does not write, but `sys_acl_set_fd` and `sys_acl_delete_def_fd` are persistence boundary declarations.

## Dependencies and Integration Points
It includes `librpc/gen_ndr/smb_acl.h` and forward-declares VFS and file structures. It is included by `smb.h` and used by VFS operations in `vfs.h`, ACL mapping code, NT security descriptor conversion, and POSIX ACL modules.

## Risks
- The comment about `mode_t` versus PIDL-generated `uint32_t` means type widths must remain compatible with generated IDL.
- Callers must honor talloc ownership of returned ACL/text objects.
- Filesystems without ACL support must be correctly detected through `no_acl_syscall_error` to avoid treating unsupported ACLs as hard failures.

## Test Signals
Useful tests include POSIX ACL get/set/delete coverage, NT ACL round trips through VFS, behavior on filesystems lacking ACL support, and compile checks for generated ACL type compatibility.
