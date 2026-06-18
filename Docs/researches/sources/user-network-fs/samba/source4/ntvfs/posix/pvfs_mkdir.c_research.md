# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_mkdir.c

Purpose: implements directory creation and removal for PVFS, including T2 mkdir with EAs, access checks, inherited ACL setup, xattr cleanup hooks, and change notifications.

Important APIs and functions: `pvfs_mkdir` handles normal `RAW_MKDIR_MKDIR` and delegates `RAW_MKDIR_T2MKDIR` to `pvfs_t2mkdir`. `pvfs_rmdir` removes directories. Both rely on `pvfs_resolve_name`, `pvfs_access_check_parent` or `pvfs_access_check_simple`, `pvfs_fileperms`, `pvfs_sys_mkdir`, `pvfs_sys_rmdir`, `pvfs_acl_inherit`, `pvfs_xattr_unlink_hook`, and `notify_trigger`.

Control flow: mkdir resolves the CIFS path, rejects existing targets, checks parent add rights, computes directory mode, creates the directory, clears stale xattr state for the path, applies inherited ACLs, and triggers directory-added notification. T2 mkdir repeats that flow, re-resolves after creation, verifies the result is a directory, applies inherited ACLs, then writes requested EAs; failures after creation remove the directory. Rmdir resolves the path, checks existence, verifies delete access, runs xattr unlink hook, calls rmdir, maps `EEXIST` to directory-not-empty, and triggers removal notification.

State and persistence: creates/removes real directories, writes inherited ACL/xattr/EA state through helper calls, and emits notify events. Rollback tries to remove partially created directories on ACL/EA failure.

Dependencies and integration points: integrates PVFS path resolution, ACL, xattr, EA, POSIX syscall wrappers, permission override, and notification subsystems.

Risks: mkdir checks `SEC_DIR_ADD_FILE` rather than add-subdir; stale xattr cleanup is required after path reuse; T2 mkdir rollback must handle partial metadata writes; rmdir maps platform-specific errors. Test signals include existing target, access denied, ACL inheritance failure rollback, T2 EA failure rollback, stale xattr cleanup, notify added/removed events, directory-not-empty mapping, and invalid mkdir levels.
