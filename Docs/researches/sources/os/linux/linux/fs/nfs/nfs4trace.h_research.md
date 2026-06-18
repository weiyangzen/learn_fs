# File Research: sources/os/linux/linux/fs/nfs/nfs4trace.h

## Purpose

`nfs4trace.h` declares the Linux tracepoint surface for NFSv4 client behavior. It covers client ID negotiation, sessions, callback handling, XDR decoding, opens, closes, locks, state recovery, delegations, namespace operations, attributes, callbacks, stateid matching, idmapping, read/write/commit, pNFS layouts, pNFS device IDs, flexfiles errors, block-layout reservation keys, and NFSv4.2 operations such as seek, fallocate, copy, clone, offload, and xattrs.

The file is a trace-event schema rather than ordinary logic. Each event defines arguments, captured fields, fast assignment code, and formatted output for ftrace/perf-style consumers.

## Trace Infrastructure

- Sets `TRACE_SYSTEM` to `nfs4`.
- Uses the normal kernel trace header guard with `TRACE_HEADER_MULTI_READ`.
- Includes generic trace helpers from `trace/misc/sunrpc.h`, `trace/misc/fs.h`, and `trace/misc/nfs.h`.
- Ends by setting `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE nfs4trace`, and including `<trace/define_trace.h>` outside the guard, matching Linux tracepoint generation conventions.
- Provides formatting helpers such as `show_nfs_fattr_flags()`, `show_nfs4_clp_state()`, `show_nfs4_state_flags()`, `show_nfs4_lock_flags()`, `show_delegation_flags()`, `show_stateid_type()`, `show_pnfs_update_layout_reason()`, `show_pr_status()`, and `show_llseek_mode()`.

## Client ID, Session, and Callback Events

`nfs4_clientid_event` is reused for client/session maintenance RPCs:

- `nfs4_setclientid`
- `nfs4_setclientid_confirm`
- `nfs4_renew`
- `nfs4_renew_async`
- `nfs4_exchange_id`
- `nfs4_create_session`
- `nfs4_destroy_session`
- `nfs4_destroy_clientid`
- `nfs4_bind_conn_to_session`
- `nfs4_sequence`
- `nfs4_reclaim_complete`

These events capture destination host and normalized NFSv4 status.

Additional session/callback events include:

- `nfs4_trunked_exchange_id`, capturing main and trunk addresses.
- `nfs4_sequence_done`, capturing session hash, slot, sequence number, highest slots, target highest slot, status flags, and error.
- `nfs4_cb_sequence` and `nfs4_cb_seqid_err`, capturing callback sequence session and slot metadata.
- `nfs4_cb_offload`, capturing callback offload filehandle, stateid, count, error, and stability mode.
- `nfs4_setup_sequence`, capturing selected slot and highest-used slot before a sequence operation.
- `pnfs_ds_connect`, capturing pNFS data-server address string and status.

## State Manager and XDR Events

- `TRACE_DEFINE_ENUM` exposes all relevant `NFS4CLNT_*` client state bits to trace formatting.
- `nfs4_state_mgr` captures hostname and formatted client state bits each time the manager iterates.
- `nfs4_state_mgr_failed` captures hostname, state bits, status, and the manager section that failed.
- `nfs4_xdr_bad_operation` captures RPC task/client identifiers, XID, decoded operation, and expected operation.
- `nfs4_xdr_event` backs `nfs4_xdr_status` and `nfs4_xdr_bad_filehandle`, capturing XDR operation and NFSv4 status.
- `nfs4_cb_error_class` backs callback authentication/client lookup failures `nfs_cb_no_clp` and `nfs_cb_badprinc`.

## Open, Close, Lock, and State Recovery Events

- `nfs4_open_event` backs `nfs4_open_reclaim`, `nfs4_open_expired`, and `nfs4_open_file`. It captures error, open flags, fmode, device, filehandle hash, fileid, parent directory id/name, open stateid, and current stateid.
- `nfs4_cached_open` records reuse of cached open state.
- `nfs4_close` records close error, current fmode, file identity, and open stateid sent to the server.
- `nfs4_lock_event` backs `nfs4_get_lock` and `nfs4_unlock`, capturing command, lock type, byte range, file identity, and stateid.
- `nfs4_set_lock` additionally captures returned lock stateid.
- State flag enums and `show_nfs4_state_flags()` expose open/delegated/reclaim/recovery/copy flags.
- `nfs4_state_lock_reclaim` records state and lock flags during recovery, helping identify lock state that could not be reclaimed.

## Delegation and Stateid Events

- `nfs4_set_delegation_event` backs `nfs4_set_delegation`, `nfs4_reclaim_delegation`, and `nfs4_detach_delegation`.
- `nfs4_delegation_event` backs `nfs_delegation_need_return`, capturing filehandle, fmode, and delegation flags.
- `nfs4_delegreturn_exit` captures delegation return status, device, filehandle, and stateid.
- `nfs4_test_stateid_event` backs `nfs4_test_delegation_stateid`, `nfs4_test_open_stateid`, and `nfs4_test_lock_stateid`.
- `nfs4_match_stateid_event` backs `nfs41_match_stateid` and `nfs4_match_stateid`, comparing stateid sequence, hash, and type for two stateids.

## Namespace, Attribute, and Callback Events

- `nfs4_lookup_event` backs lookup-like operations: `nfs4_lookup`, `nfs4_symlink`, `nfs4_mkdir`, `nfs4_mknod`, `nfs4_remove`, `nfs4_get_fs_locations`, and `nfs4_secinfo`.
- `nfs4_lookupp` records parent lookup results.
- `nfs4_rename` captures old and new directory/file names and error status.
- `nfs4_inode_event` backs inode-only operations: `nfs4_access`, `nfs4_readlink`, `nfs4_readdir`, `nfs4_get_acl`, `nfs4_set_acl`, and conditionally security label get/set events.
- `nfs4_inode_stateid_event` backs stateid-sensitive inode operations: `nfs4_setattr`, `nfs4_delegreturn`, stateid update/wait/skip events, and several pNFS layout operations.
- `nfs4_getattr_event` backs `nfs4_getattr`, `nfs4_lookup_root`, and `nfs4_fsinfo`, including fattr valid-bit formatting.
- `nfs4_inode_callback_event` backs `nfs4_cb_getattr`.
- `nfs4_inode_stateid_callback_event` backs `nfs4_cb_recall` and `nfs4_cb_layoutrecall_file`.

## ID Mapping Events

`nfs4_idmap_event` backs:

- `nfs4_map_name_to_uid`
- `nfs4_map_group_to_gid`
- `nfs4_map_uid_to_name`
- `nfs4_map_gid_to_group`

It captures the mapped name, id, and status. The dynamic string array defensively handles negative lengths by tracing an empty string.

## Read, Write, Commit, and pNFS Layout Events

- `nfs4_read_event` backs `nfs4_read` and `nfs4_pnfs_read`, capturing file identity, offset, requested/resolved byte counts, open stateid, layout stateid, and error.
- `nfs4_write_event` backs `nfs4_write` and `nfs4_pnfs_write`, with analogous write payload fields.
- `nfs4_commit_event` backs `nfs4_commit` and `nfs4_pnfs_commit_ds`, capturing commit offset/count and layout stateid.
- `nfs4_layoutget` captures layout request and result stateid for pNFS layout acquisition.
- `nfs4_layoutcommit`, `nfs4_layoutreturn`, `nfs4_layoutreturn_on_close`, `nfs4_layouterror`, and `nfs4_layoutstats` reuse the inode/stateid event class.
- `pnfs_update_layout` captures update-layout inputs, cached/returned segment pointer, layout stateid if valid, and an enum reason such as no pNFS, retry, blocked, cached, or sent layoutget.
- `pnfs_layout_event` backs metadata-server fallback events for page-init read/write, mirror count, read/write completion, and read/write pagelist paths.

## pNFS Device, Flexfiles, and Block Layout Events

- `nfs4_deviceid_event` backs `nfs4_deviceid_free`, capturing destination address and raw deviceid bytes.
- `nfs4_deviceid_status` backs `nfs4_getdeviceinfo` and `nfs4_find_deviceid`, capturing server device, destination address, deviceid bytes, and status.
- `fl_getdevinfo` captures file-layout MDS address, deviceid, and data-server IP string.
- `nfs4_flexfiles_io_event` backs `ff_layout_read_error` and `ff_layout_write_error`, capturing local error, server NFS error, file identity, offset/count, stateid, and data-server address.
- `ff_layout_commit_error` records analogous flexfiles commit error information.
- `bl_ext_tree_prepare_commit` records block-layout extent-tree commit preparation result, range count, last written byte, and whether all ranges were encoded.
- `pnfs_bl_pr_key_class` backs `bl_pr_key_reg` and `bl_pr_key_unreg`, recording block device and persistent reservation key.
- `pnfs_bl_pr_key_err_class` backs `bl_pr_key_reg_err` and `bl_pr_key_unreg_err`, adding a formatted persistent reservation status.

## NFSv4.2 Conditional Events

When `CONFIG_NFS_V4_2` is enabled, the header adds events for newer protocol operations:

- `nfs4_llseek` for `SEEK_DATA`/`SEEK_HOLE`, recording input offset, result offset, EOF, stateid, and mode.
- `nfs4_sparse_event` backs `nfs4_fallocate` and `nfs4_deallocate`, capturing range and stateid.
- `nfs4_copy` captures intra-server or inter-server copy details, source/destination file identities, stateids, offsets, length, sync mode, callback/result stateid, result count, and consistency flags.
- `nfs4_clone` captures clone source/destination identities, offsets, length, and stateids.
- `nfs4_copy_notify` captures source copy-notify stateid and returned stateid.
- `nfs4_offload_class` backs `nfs4_offload_cancel` and `nfs4_offload_status`.
- `nfs4_xattr_event` backs `nfs4_getxattr`, `nfs4_setxattr`, and `nfs4_removexattr`.
- `nfs4_listxattr` reuses the inode event class.

## Cross-File Relationships

- `nfs4trace.c` materializes these tracepoints and exports selected pNFS-related tracepoint symbols.
- `nfs4state.c` emits state-manager and lock-reclaim tracepoints during recovery.
- NFSv4 XDR, proc, delegation, callback, pNFS, layout-driver, idmap, and NFSv4.2 operation files include this header to emit protocol-specific events.
- The tracepoint payloads depend on NFS helper hash/format functions such as `nfs_fhandle_hash()`, `nfs_stateid_hash()`, `nfs_session_id_hash()`, `show_nfs4_status()`, `show_fs_fmode_flags()`, and pNFS formatting helpers.

## Research Notes

The header is organized around reusable event classes to avoid duplicating common payloads. A useful mental model is: client/session state first, VFS/protocol operations next, pNFS/layout diagnostics after that, and optional NFSv4.2 features at the end. It is the primary observability contract for diagnosing NFSv4 client state, recovery, I/O, callback, layout, and copy/offload behavior.
