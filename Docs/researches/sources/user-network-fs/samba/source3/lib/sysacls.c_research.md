## sources/user-network-fs/samba/source3/lib/sysacls.c

Purpose: Samba system ACL abstraction. It provides a normalized `sys_acl_*` interface over Samba’s internal `struct smb_acl_t` and dispatches fd ACL operations to the platform’s default VFS ACL backend when compiled.

Important APIs include ACL entry iteration and inspection (`sys_acl_get_entry`, `sys_acl_get_tag_type`, `sys_acl_get_permset`, `sys_acl_get_qualifier`, `sys_acl_get_perm`), construction/mutation (`sys_acl_init`, `sys_acl_create_entry`, `sys_acl_set_tag_type`, `sys_acl_set_qualifier`, `sys_acl_clear_perms`, `sys_acl_add_perm`, `sys_acl_set_permset`), rendering (`sys_acl_to_text`), fd operations (`sys_acl_get_fd`, `sys_acl_set_fd`, `sys_acl_delete_def_fd`), and `no_acl_syscall_error`.

Control flow: callers build an ACL with `sys_acl_init`, append entries, set tag/qualifier/permission fields, and pass it to VFS-backed setters. Iteration uses `acl_d->next`, reset by `SMB_ACL_FIRST_ENTRY`, then advanced by `SMB_ACL_NEXT_ENTRY`. fd operations compile-time dispatch to POSIX, AIX, Solaris/UnixWare, HPUX, or no-ACL stubs returning `ENOTSUP`/`ENOSYS`.

State and persistence: ACL structures are talloc-owned and memory-only until passed to backend setters, which persist ACLs on filesystem objects. Dependencies are platform ACL modules, passwd/group name lookups, talloc, VFS handle/files structures, and Samba debug classes.

Risks: `SMB_ACL_ENTRY_T` pointers become unstable after operations that may reorder/reallocate ACL entries, as the file comment warns. `sys_acl_get_tag_type` and similar accessors do little NULL validation. Rendering uses passwd/group lookups and can return numeric group IDs when lookup fails. Tests should exercise backend dispatch, no-ACL errno recognition, ACL text output, invalid tags/perms, iteration order, and descriptor invalidation assumptions.
