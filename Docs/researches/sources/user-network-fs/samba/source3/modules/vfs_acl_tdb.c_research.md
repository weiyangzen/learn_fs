<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_acl_tdb.c -->
# sources/user-network-fs/samba/source3/modules/vfs_acl_tdb.c

## Purpose
This VFS module stores Windows NT ACL blobs in Samba's state TDB `file_ntacls.tdb`, keyed by filesystem file id. It is one backend for `vfs_acl_common.c`, useful when NT ACLs should be preserved without relying on per-file xattrs.

## Important APIs, Types, And Functions
The module registers as `acl_tdb`. Key functions are `acl_tdb_init`, `disconnect_acl_tdb`, `acl_tdb_delete`, backend callbacks `fget_acl_blob` and `store_acl_blob_fsp`, `unlinkat_acl_tdb`, `connect_acl_tdb`, `sys_acl_set_fd_tdb`, `acl_tdb_fget_nt_acl`, and `acl_tdb_fset_nt_acl`. It uses static `ref_count` and `struct db_context *acl_db`.

## Control Flow
Connect calls the next VFS connect, opens the state database as root if needed, initializes common config, and forces share parameters such as `inherit acls`, `dos filemode`, and `force unknown acl user`. If `ignore system acls` is set, it also relaxes create/directory masks, disables DOS attribute mapping, and enables stored DOS attributes. Get/set delegate to `fget_nt_acl_common` and `fset_nt_acl_common` using TDB fetch/store callbacks. Unlink/rmdir go through common delete behavior, then delete the TDB record for non-stream objects. Direct lower POSIX ACL sets delete the stored NT ACL unless they are part of a guarded NT ACL set.

## State And Persistence
NT ACL blobs are persisted in `state_path("file_ntacls.tdb")`. Records use the backwards-compatible 16-byte dev/inode file id from `push_file_id_16`, which means data follows inode identity rather than path. The database is process-global with reference counting and closes when the last share disconnects.

## Dependencies And Integration Points
Dependencies include dbwrap/TDB, Samba state paths, VFS file-id helpers, common ACL helpers, auth/loadparm, and lower VFS ACL/unlink calls. It integrates with Samba's module stack through `vfs_fn_pointers` for connect, disconnect, unlinkat, fchmod, NT ACL get/set, and sys ACL set.

## Risks
Keying by dev/inode is compatible but can leave stale records after inode reuse if delete cleanup is missed. Named streams intentionally do not carry separate stored ACLs. Database open failures disable the module connect. Refcounting is static process state and must remain balanced across failed connect/disconnect paths.

## Test Signals
Tests should cover database creation, fetch/store by file id, delete-on-unlink/rmdir, named stream no-op cleanup, common ACL hash behavior through this backend, direct POSIX ACL set invalidating stored ACLs, and disconnect closing the TDB at refcount zero.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_acl_tdb.c -->
