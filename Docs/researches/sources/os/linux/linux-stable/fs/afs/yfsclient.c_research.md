# File Research: sources/os/linux/linux-stable/fs/afs/yfsclient.c

## Purpose
Implements kAFS client-side YFS file-server RPC stubs. It builds YFS XDR requests, unmarshals replies, and connects YFS operations to the common `afs_operation` / `afs_call` machinery.

## Main Interfaces
- File data and metadata: `yfs_fs_fetch_data()`, `yfs_fs_store_data()`, `yfs_fs_fetch_status()`, `yfs_fs_setattr()`.
- Namespace operations: `yfs_fs_create_file()`, `yfs_fs_make_dir()`, `yfs_fs_remove_file()`, `yfs_fs_remove_dir()`, `yfs_fs_link()`, `yfs_fs_symlink()`.
- Rename variants: `yfs_fs_rename()`, `yfs_fs_rename_replace()`, `yfs_fs_rename_noreplace()`, `yfs_fs_rename_exchange()`.
- Volume and locking: `yfs_fs_get_volume_status()`, `yfs_fs_set_lock()`, `yfs_fs_extend_lock()`, `yfs_fs_release_lock()`.
- Bulk status and ACLs: `yfs_fs_inline_bulk_status()`, `yfs_fs_fetch_opaque_acl()`, `yfs_fs_store_opaque_acl2()`, `yfs_free_opaque_acl()`.

## Implementation Notes
The file is dominated by XDR helpers for YFS fids, strings, store status records, volume status, callbacks, volsync records, and 100ns YFS timestamp conversion. Reply delivery functions decode status/callback/volsync combinations into `afs_status_cb` and operation result fields.

Fetch-data delivery is a staged unmarshalling state machine: it extracts returned data length, transfers file data into the netfs subrequest iterator, discards excess server data if needed, then decodes status, callback, and volume sync metadata.

YFS optional operation support is probed by failure. `YFS.RemoveFile2` and `YFS.Rename_Replace` downgrade to older operations by setting server capability flags when the server returns unsupported-operation abort codes.

## Cross-File Relationships
Depends on AFS/YFS protocol structures from `afs_fs.h`, `xdr_fs.h`, and `protocol_yfs.h`, and on the AFS operation/call framework from `internal.h`. Status results feed common kAFS vnode, callback, volume sync, lock, and netfs paths.

## Risks / Review Notes
Request buffer sizing is manually matched to encoded fields and checked only after encoding by `yfs_check_req()`. Reply length/state sequencing is protocol-sensitive, especially for variable-length volume status strings and opaque ACL payloads. Rename and remove downgrade behavior is per-server state and affects later operation selection.
