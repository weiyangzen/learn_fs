# File Research: sources/os/linux/linux-stable/fs/afs/fsclient.c

## Summary
Implements AFS fileserver RPC client stubs. It encodes requests, decodes XDR replies, defines call types, and bridges high-level `afs_operation` requests to rxrpc calls for status, data I/O, namespace mutation, attributes, locks, capabilities, bulk status, and ACLs.

## Main Responsibilities
- Decodes common AFS XDR records: FIDs, fetch status, callbacks, volsync, and volume status.
- Encodes store-status attributes and request payloads.
- Implements `FS.FetchStatus`, `FS.FetchData`, and `FS.FetchData64`.
- Implements create, mkdir, remove, link, symlink, rename, store data, and setattr RPCs.
- Implements volume status, lock, callback give-up, capability probe, inline bulk status, fetch ACL, and store ACL RPCs.
- Defines `struct afs_call_type` instances for each RPC family.

## Key APIs
- `afs_fs_fetch_status()`.
- `afs_fs_fetch_data()`.
- `afs_fs_create_file()`, `afs_fs_make_dir()`.
- `afs_fs_remove_file()`, `afs_fs_remove_dir()`.
- `afs_fs_link()`, `afs_fs_symlink()`, `afs_fs_rename()`.
- `afs_fs_store_data()`, `afs_fs_setattr()`.
- `afs_fs_get_volume_status()`.
- `afs_fs_set_lock()`, `afs_fs_extend_lock()`, `afs_fs_release_lock()`.
- `afs_fs_give_up_all_callbacks()`.
- `afs_fs_get_capabilities()`.
- `afs_fs_inline_bulk_status()`.
- `afs_fs_fetch_acl()`, `afs_fs_store_acl()`.

## Important Behavior
Fetch-data decoding is phased: it reads the returned length, streams data directly into the netfs subrequest iterator, discards excess if needed, then decodes status/callback/volsync metadata. 64-bit fetch/store variants are selected when `AFS_SERVER_FL_HAS_FS64` is set.

Setattr with size changes uses `FS.StoreData`/`FS.StoreData64` with zero write size so file length can be changed; metadata-only setattr uses `FS.StoreStatus`.

`FS.GetCapabilities` is asynchronous and used by probe code. Its call type reports results through `afs_fileserver_probe_result()` and frees endpoint-state references in its destructor.

`FS.InlineBulkStatus` validates returned status and callback counts against `op->nr_files`; if the server returns invalid operation, the server and volume are marked as maybe lacking inline bulk support.

## State and Synchronization
Each RPC allocates an `afs_call`, fills `call->request`, assigns the primary FID for tracing, and dispatches with `afs_make_op_call()` or `afs_make_call()`. Reply decoding populates `op->file[]`, `op->more_files[]`, `op->volsync`, `op->volstatus`, or ACL pointers.

## Risks
Manual XDR sizing and padding are pervasive. A mismatch between allocated request/reply sizes and encoded fields can corrupt protocol handling. Inline bulk status has known interoperability handling for older OpenAFS status-version behavior and missing support.
