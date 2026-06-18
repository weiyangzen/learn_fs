# File Research: sources/os/linux/linux/fs/afs/fsclient.c

## Purpose
Implements AFS fileserver RPC client stubs and XDR marshalling/unmarshalling for AFS3 file service operations.

## Main Responsibilities
- Encodes requests and decodes replies for file status, data fetch/store, create/remove/link/symlink/rename, setattr, volume status, locks, callbacks, capabilities, inline bulk status, and ACL operations.
- Defines `afs_call_type` descriptors used by the RxRPC layer and `afs_operation` dispatcher.
- Handles streaming reply state machines for variable-sized or data-bearing replies.
- Selects 32-bit or 64-bit file data RPCs based on server capability.
- Reports protocol errors for malformed status, bad counts, or oversized strings.

## Key Functions and Data
- XDR helpers: `xdr_decode_AFSFid()`, `xdr_decode_AFSFetchStatus()`, `xdr_decode_AFSCallBack()`, `xdr_decode_AFSVolSync()`, `xdr_encode_AFS_StoreStatus()`, and `xdr_decode_AFSFetchVolumeStatus()`.
- Status/data RPCs: `afs_fs_fetch_status()`, `afs_fs_fetch_data()`, `afs_fs_fetch_data64()`.
- Mutation RPCs: `afs_fs_create_file()`, `afs_fs_make_dir()`, `afs_fs_remove_file()`, `afs_fs_remove_dir()`, `afs_fs_link()`, `afs_fs_symlink()`, `afs_fs_rename()`.
- Write/setattr RPCs: `afs_fs_store_data()`, `afs_fs_store_data64()`, `afs_fs_setattr()`, and size-specific StoreData variants.
- Lock RPCs: `afs_fs_set_lock()`, `afs_fs_extend_lock()`, `afs_fs_release_lock()`.
- Probe/capability RPCs: `afs_fs_get_capabilities()` and `afs_deliver_fs_get_capabilities()`.
- Bulk/ACL RPCs: `afs_fs_inline_bulk_status()`, `afs_fs_fetch_acl()`, and `afs_fs_store_acl()`.

## Important Details
- `xdr_decode_AFSFetchStatus()` accepts the OpenAFS `InlineBulkStatus` zero-version error quirk when an inline abort code is present.
- `FS.FetchData` delivery first extracts a returned data length, streams payload into the netfs subrequest iterator, discards excess, then decodes status/callback/volsync.
- `FS.GetVolumeStatus` parses multiple padded strings and bounds them with `AFSNAMEMAX`.
- `FS.GetCapabilities` is asynchronous and reports results through probe callbacks; its destructor drops the endpoint-state reference.
- `FS.InlineBulkStatus` validates returned status and callback counts against `op->nr_files`; unsupported servers set `AFS_SERVER_FL_NO_IBULK`.
- ACL fetch allocates a flexible `afs_acl` payload sized from the server-returned opaque ACL length.
