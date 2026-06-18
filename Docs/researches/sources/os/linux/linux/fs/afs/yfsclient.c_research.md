# File Research: sources/os/linux/linux/fs/afs/yfsclient.c

## Summary
Implements YFS file-server client RPC stubs for the Linux AFS client. It marshals YFS requests, unmarshals replies, updates AFS operation status/callback state, and provides YFS variants of file, directory, lock, volume-status, and ACL operations.

## Main Responsibilities
- Encode/decode YFS XDR primitives, FIDs, store status records, timestamps, callbacks, volume status, and file status.
- Build and issue YFS RPC calls through `afs_alloc_flat_call()` and `afs_make_op_call()`.
- Deliver replies for fetch/store/status/mutation/lock/ACL operations.
- Handle server capability downgrade for `RemoveFile2` and extended rename operations.
- Support streaming data extraction for `YFS.FetchData64`.
- Support opaque ACL fetch/store operations.

## Key APIs
- `yfs_fs_fetch_data()`, `yfs_fs_store_data()`.
- `yfs_fs_create_file()`, `yfs_fs_make_dir()`, `yfs_fs_remove_file()`, `yfs_fs_remove_dir()`.
- `yfs_fs_link()`, `yfs_fs_symlink()`, `yfs_fs_rename()`, `yfs_fs_rename_replace()`, `yfs_fs_rename_noreplace()`, `yfs_fs_rename_exchange()`.
- `yfs_fs_setattr()`, `yfs_fs_fetch_status()`, `yfs_fs_inline_bulk_status()`.
- `yfs_fs_get_volume_status()`.
- `yfs_fs_set_lock()`, `yfs_fs_extend_lock()`, `yfs_fs_release_lock()`.
- `yfs_fs_fetch_opaque_acl()`, `yfs_fs_store_opaque_acl2()`, `yfs_free_opaque_acl()`.

## Important Behavior
YFS timestamps are 64-bit 100ns units and are converted to/from Linux `timespec64`, with special handling for negative values on 32-bit builds.

`YFS.FetchData64` is delivered as a multi-stage state machine: length, data into the netfs subrequest iterator, excess discard, then status/callback/volsync metadata. EOF is marked when transferred bytes reach the returned status size.

Create, mkdir, symlink, link, remove, rename, store, setattr, lock, and status calls use hand-computed request and reply sizes. `yfs_check_req()` warns if the encoded request length does not exactly match the allocated buffer.

`yfs_fs_remove_file()` first tries `YFS.RemoveFile2` unless the server is marked as lacking it. `yfs_done_fs_remove_file2()` sets `AFS_SERVER_FL_NO_RM2` and marks the operation for downgrade on unsupported-op aborts.

`yfs_fs_rename()` similarly prefers `YFS.Rename_Replace` unless the server is marked `AFS_SERVER_FL_NO_RENAME2`; the extended rename paths can return displaced target status.

## State and Lifetime
The file operates around `struct afs_operation`, `struct afs_call`, `struct afs_vnode_param`, status/callback records, and operation-specific embedded state. ACL fetch allocates `struct afs_acl` buffers into `op->yacl`; `yfs_free_opaque_acl()` owns cleanup.

## Risks
XDR sizes, padding, and decode order are manually maintained and must match the protocol exactly. The streaming fetch path mutates `call->iter`, `iov_len`, `remaining`, and netfs subrequest counters across delivery states. ACL lengths come from the server and drive allocations after rounding. Feature downgrade depends on correctly interpreting RX abort codes.
