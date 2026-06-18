<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aixacl.c -->
# sources/user-network-fs/samba/source3/modules/vfs_aixacl.c

## Purpose
This VFS module exposes classic AIX ACLs through Samba's POSIX ACL abstraction. It implements file-descriptor get/set hooks using AIX `fstatacl`, `fchacl`, and `chacl`, with conversion delegated to `vfs_aixacl_util.c`.

## Important APIs, Types, And Functions
The exported VFS helpers are `aixacl_sys_acl_get_fd`, `aixacl_sys_acl_set_fd`, and `aixacl_sys_acl_delete_def_fd`. The module registers `sys_acl_get_fd_fn`, `sys_acl_blob_get_fd_fn`, `sys_acl_set_fd_fn`, and `sys_acl_delete_def_fd_fn` under module name `aixacl`.

## Control Flow
Get rejects default ACL requests because classic AIX has no default ACL. It allocates an initial `BUFSIZ` `struct acl`, calls `fstatacl`, reallocates to `file_acl->acl_len + sizeof(struct acl)` on `ENOSPC`, then converts the AIX ACL to `SMB_ACL_T`. Set converts `SMB_ACL_T` to AIX ACL. For pathref fsp objects it calls path-based `chacl`; otherwise it calls `fchacl` on the I/O fd. Delete-default returns success so upper layers can proceed.

## State And Persistence
The module persists ACL changes directly to the AIX filesystem via `chacl`/`fchacl`. It has no module-private durable state.

## Dependencies And Integration Points
Dependencies include AIX ACL system calls and structures, Samba VFS/fsp helpers, `posix_sys_acl_blob_get_fd`, and conversion helpers from `vfs_aixacl_util.h`. It is a platform-specific adapter in Samba's VFS ACL stack.

## Risks
Default ACLs are unsupported but reported as successful for delete-default. The get path must correctly size variable-length AIX ACL structures after `ENOSPC`. The pathref set path is no longer handle-based and uses the base path, so path stability and symlink semantics depend on surrounding Samba pathref guarantees.

## Test Signals
Platform tests on AIX should cover access ACL get/set, `ENOSPC` resize, pathref and fd set paths, default ACL request rejection, delete-default success, and round-trip conversion through `aixacl_to_smbacl` and `aixacl_smb_to_aixacl`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aixacl.c -->
