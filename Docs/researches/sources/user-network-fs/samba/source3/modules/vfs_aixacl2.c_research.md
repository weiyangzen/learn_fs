<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aixacl2.c -->
# sources/user-network-fs/samba/source3/modules/vfs_aixacl2.c

## Purpose
This VFS module supports AIX JFS2 ACLs, including NFSv4 ACLs and AIXC POSIX-like ACLs. It converts JFS2 NFSv4 ACL data to Samba's NFSv4 ACL abstraction for NT ACL operations and falls back to POSIX ACL paths where NFSv4 ACLs are unavailable.

## Important APIs, Types, And Functions
The file defines `AIXJFS2_ACL_T` as a union over `nfs4_acl_int_t` and `aixc_acl_t`. Important helpers are `aixacl2_getlen`, `aixjfs2_getacl_alloc`, `aixjfs2_get_nfs4_acl`, `aixjfs2_fget_nt_acl`, `aixjfs2_sys_acl_blob_get_fd`, `aixjfs2_get_posix_acl`, `aixjfs2_sys_acl_get_fd`, `aixjfs2_query_acl_support`, `aixjfs2_process_smbacl`, `aixjfs2_set_nt_acl_common`, `aixjfs2_fset_nt_acl`, `aixjfs2_sys_acl_set_fd`, and `aixjfs2_sys_acl_delete_def_fd`.

## Control Flow
ACL allocation starts with `aclx_get`, optionally querying type info with `GET_ACLINFO_ONLY`, then reallocates based on ACL length on `ENOSPC`. Get NT ACL attempts an NFSv4 JFS2 ACL read, converts each `nfs4_ace_int_t` into `SMB_ACE4PROP_T`, and calls `smb_fget_nt_acl_nfs4`; `ENOSYS` triggers fallback to `posix_fget_nt_acl`. Set NT ACL first queries whether `ACL_NFS4` is supported; if so, `smb_set_nt_acl_nfs4` calls back into `aixjfs2_process_smbacl`, which linearizes Samba NFSv4 ACEs into JFS2 `nfs4_acl_int_t` and writes them with `aclx_put`. Without NFSv4 support, it falls back to `set_nt_acl`. POSIX ACL get/set paths use AIXC ACL type and conversion helpers.

## State And Persistence
ACLs are persisted directly in the AIX JFS2 filesystem using `aclx_get`, `aclx_put`, and `aclx_fput`. The module has no private persistent database. Temporary ACL allocations are talloc-based.

## Dependencies And Integration Points
Dependencies include AIX JFS2 ACL APIs and types, Samba NFSv4 ACL conversion (`nfs4_acls.h`), POSIX ACL fallback helpers, AIX classic conversion helpers, and VFS stat wrappers `nfs4_acl_stat/fstat/lstat/fstatat`. It registers as `aixacl2`.

## Risks
The code stores numeric `who.id` values and does not serialize textual NFSv4 principals. `sys_acl_blob_get_fd` cannot linearize NFSv4 ACLs and returns `ENOSYS`, limiting common hash validation. Query failures are mapped from errno, while lack of NFSv4 support assumes POSIX fallback. Entry length alignment and ACL length calculations must match AIX kernel structure expectations.

## Test Signals
AIX JFS2 tests should cover NFSv4 ACL get/set, AIXC ACL get/set, fallback from `ENOSYS` to POSIX ACLs, `aclx_gettypes` support detection, pathref versus fd set paths, ACE count/entry length alignment, and NT ACL conversion through Samba's NFSv4 ACL helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aixacl2.c -->
