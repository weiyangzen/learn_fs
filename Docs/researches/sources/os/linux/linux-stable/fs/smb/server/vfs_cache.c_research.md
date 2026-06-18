# File Research: sources/os/linux/linux-stable/fs/smb/server/vfs_cache.c

## Summary
Implements ksmbd open-file and inode caching: per-session volatile FID tables, global durable/persistent handle tables, inode-open lists, delete-on-close state, lock cleanup, durable handle preservation/reconnect, durable scavenging, open-file proc reporting, and file-cache lifecycle.

## Main Responsibilities
- Maintain a global inode hash mapping dentries to `struct ksmbd_inode`.
- Track per-inode open file lists, oplock lists, delete-pending/delete-on-close flags, and file attributes.
- Allocate and free `struct ksmbd_file` objects from a kmem cache.
- Allocate volatile ids in per-session file tables and persistent ids in the global durable table using IDR.
- Enforce a configured open-file limit.
- Lookup file handles by volatile id, persistent id, create GUID, or inode/dentry.
- Close file handles, cancel blocked works, remove oplocks, release byte-range locks, drop connection refs, free stream/owner strings, and `fput()` files.
- Handle delete-on-close for files and named streams.
- Preserve reconnectable durable/resilient/persistent handles across session teardown.
- Run a durable-handle scavenger kthread that expires preserved handles after timeout.
- Reopen durable handles onto a new connection/session and restore lock/oplock connection associations.
- Validate durable reconnect names and owner identity.
- Close all handles for a tree connection or session.

## Key Interfaces
- Table lifecycle: `ksmbd_init_file_table()`, `ksmbd_destroy_file_table()`, `ksmbd_init_global_file_table()`, `ksmbd_free_global_file_table()`.
- Open/close/lookup: `ksmbd_open_fd()`, `ksmbd_close_fd()`, `ksmbd_fd_put()`, `ksmbd_lookup_fd_fast()`, `ksmbd_lookup_fd_slow()`, `ksmbd_lookup_global_fd()`, `ksmbd_lookup_durable_fd()`, `ksmbd_lookup_fd_cguid()`, `ksmbd_lookup_fd_inode()`.
- Durable handles: `ksmbd_open_durable_fd()`, `ksmbd_reopen_durable_fd()`, `ksmbd_put_durable_fd()`, `ksmbd_launch_ksmbd_durable_scavenger()`, `ksmbd_stop_durable_scavenger()`, `ksmbd_validate_name_reconnect()`, `ksmbd_vfs_compare_durable_owner()`.
- Inode/delete state: `ksmbd_inode_lookup_lock()`, `ksmbd_inode_put()`, `ksmbd_query_inode_status()`, `ksmbd_inode_pending_delete()`, `ksmbd_set_inode_pending_delete()`, `ksmbd_clear_inode_pending_delete()`, `ksmbd_fd_set_delete_on_close()`.

## Important Behavior
Each open file owns a strong connection reference while `fp->conn` is non-NULL. Session teardown can detach reconnectable durable handles by clearing `conn`, `tcon`, and `volatile_id`, removing them from the session table, and leaving them reachable through the global durable table until reconnect or scavenger expiry.

Close paths distinguish volatile table removal, durable table removal, inode-list unlink, final reference drop, and delayed finalization. Several comments document race fixes around FP_NEW/FP_INITED transitions, stale IDR ids, m_fp_list walkers, and open-file counter accounting.

A handle is reconnectable only if it is resilient/persistent, or durable with lease handle caching, or durable with batch oplock, and its oplock state is not in transition. Durable reconnect verifies owner uid/gid/name and can validate the path name relative to the share.

## Cross-File Interactions
Interacts with VFS deletion/unlink, oplock state, connection/session/tree management, SMB2 durable handle create/reconnect contexts, byte-range lock tracking, and proc debug output.

## Risks
This file is highly concurrency-sensitive. IDR publication/removal, refcount transitions, durable session teardown, scavenger expiry, inode list walking, connection reference ownership, delete-on-close, and open-file accounting all have race-prone edge cases.
