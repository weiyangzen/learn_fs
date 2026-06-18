# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4trace.h

## Purpose

`nfs4trace.h` defines the Linux kernel tracepoint surface for the NFSv4 client. It covers clientid/session operations, state-manager execution, XDR errors, callbacks, open/close/lock, delegations, stateid tests, directory and inode operations, idmapping, read/write/commit I/O, pNFS layouts/devices, flexfiles, block layout persistent reservations, and NFSv4.2 operations.

It is included normally by users and included with `CREATE_TRACE_POINTS` by `nfs4trace.c` to instantiate tracepoints.

## Header Structure

The file sets:
- `TRACE_SYSTEM nfs4`
- include guard `_TRACE_NFS4_H`
- includes for tracepoint core and shared SUNRPC/NFS formatting helpers
- local `delegation.h`

At the end it sets:
- `TRACE_INCLUDE_PATH .`
- `TRACE_INCLUDE_FILE nfs4trace`
- includes `<trace/define_trace.h>` outside the guard, as required by kernel tracepoint headers.

## Shared Formatting Helpers

The header defines symbolic/flag printers for:
- NFS fattr valid bits: `show_nfs_fattr_flags`
- NFSv4 client state bits: `show_nfs4_clp_state`
- NFSv4 open/lock state flags: `show_nfs4_state_flags`, `show_nfs4_lock_flags`
- delegation flags: `show_delegation_flags`
- stateid type: `show_stateid_type`
- pNFS layout update reason: `show_pnfs_update_layout_reason`
- block persistent reservation status: `show_pr_status`
- NFSv4.2 llseek mode: `show_llseek_mode`

It also uses shared helpers such as `show_nfs4_status`, `show_fs_fmode_flags`, `show_fs_fcntl_open_flags`, `show_fs_fcntl_cmd`, `show_fs_fcntl_lock_type`, and `show_pnfs_layout_iomode`.

Most events log compact file identity using:
- device major/minor,
- NFS fileid,
- hashed file handle,
- stateid sequence and stateid hash.

## Client ID and Session Events

`nfs4_clientid_event` is reused for:
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

These events log destination address and decoded NFSv4 status.

Dedicated session/client events include:
- `nfs4_trunked_exchange_id`: logs main and trunk addresses.
- `nfs4_sequence_done`: logs session hash, slot number, seq number, slot targets, status flags, and error.
- `nfs4_setup_sequence`: logs slot setup state before sending a sequence operation.

## Callback Events

Callback tracepoints include:
- `nfs4_cb_sequence`
- `nfs4_cb_seqid_err`
- `nfs4_cb_offload`
- `nfs_cb_no_clp`
- `nfs_cb_badprinc`
- `nfs4_cb_getattr`
- `nfs4_cb_recall`
- `nfs4_cb_layoutrecall_file`

They log callback XIDs, callback identifiers, session/slot data, file handles, stateids, target client hostname where available, and NFSv4 status.

## State Manager Events

The header exposes all relevant `NFS4CLNT_*` bits via `TRACE_DEFINE_ENUM`, then defines:
- `nfs4_state_mgr`
- `nfs4_state_mgr_failed`

`nfs4_state_mgr` logs hostname and decoded client state bitset.

`nfs4_state_mgr_failed` logs hostname, decoded client state bitset, decoded error, and the state-manager section that failed. This is used directly by `nfs4state.c`.

## XDR Error Events

XDR tracepoints include:
- `nfs4_xdr_bad_operation`
- `nfs4_xdr_status`
- `nfs4_xdr_bad_filehandle`

They log SUNRPC task/client IDs, XID, operation number, expected operation, and decoded error status. These are diagnostic events for COMPOUND result decoding failures or unexpected server replies.

## Open, Close, and Lock Events

Open events:
- `nfs4_open_reclaim`
- `nfs4_open_expired`
- `nfs4_open_file`
- `nfs4_cached_open`

They log open flags, file mode, parent/file identity, open stateid, and current stateid.

Close event:
- `nfs4_close`

Lock events:
- `nfs4_get_lock`
- `nfs4_unlock`
- `nfs4_set_lock`

They log command, lock type, byte range, file identity, open stateid, and lock stateid for set-lock.

State reclaim tracepoint:
- `nfs4_state_lock_reclaim`

It logs open state flags and lock flags, and is used in `nfs4state.c` to diagnose unrecovered lock state.

## Delegation and Stateid Events

Delegation events:
- `nfs4_set_delegation`
- `nfs4_reclaim_delegation`
- `nfs4_detach_delegation`
- `nfs_delegation_need_return`
- `nfs4_delegreturn_exit`

Stateid test/update events:
- `nfs4_test_delegation_stateid`
- `nfs4_test_open_stateid`
- `nfs4_test_lock_stateid`
- `nfs4_setattr`
- `nfs4_delegreturn`
- `nfs4_open_stateid_update`
- `nfs4_open_stateid_update_wait`
- `nfs4_open_stateid_update_skip`
- `nfs4_close_stateid_update_wait`

Stateid comparison events:
- `nfs41_match_stateid`
- `nfs4_match_stateid`

These are focused on stateid sequence/hash/type diagnostics and delegation lifecycle visibility.

## Directory, Metadata, and Inode Events

Lookup-style events:
- `nfs4_lookup`
- `nfs4_symlink`
- `nfs4_mkdir`
- `nfs4_mknod`
- `nfs4_remove`
- `nfs4_get_fs_locations`
- `nfs4_secinfo`
- `nfs4_lookupp`
- `nfs4_rename`

Inode operation events:
- `nfs4_access`
- `nfs4_readlink`
- `nfs4_readdir`
- `nfs4_get_acl`
- `nfs4_set_acl`
- optionally `nfs4_get_security_label`
- optionally `nfs4_set_security_label`

Getattr-like events:
- `nfs4_getattr`
- `nfs4_lookup_root`
- `nfs4_fsinfo`

These events consistently log decoded errors and stable file/directory identifiers.

## ID Mapping Events

`nfs4_idmap_event` is reused for:
- `nfs4_map_name_to_uid`
- `nfs4_map_group_to_gid`
- `nfs4_map_uid_to_name`
- `nfs4_map_gid_to_group`

It logs mapping name, ID, and decoded error. It dynamically sizes the name buffer and null-terminates it after copying.

## Read, Write, and Commit Events

I/O event classes define:
- `nfs4_read`
- `nfs4_pnfs_read`
- `nfs4_write`
- `nfs4_pnfs_write`
- `nfs4_commit`
- `nfs4_pnfs_commit_ds`

They log:
- file identity and file handle,
- offset and requested/result count,
- NFSv4 stateid sequence/hash,
- pNFS layout stateid sequence/hash when present,
- decoded NFSv4 error.

The pNFS variants are exported by `nfs4trace.c`.

## pNFS Layout Events

Layout tracepoints include:
- `nfs4_layoutget`
- `nfs4_layoutcommit`
- `nfs4_layoutreturn`
- `nfs4_layoutreturn_on_close`
- `nfs4_layouterror`
- `nfs4_layoutstats`
- `pnfs_update_layout`

`pnfs_update_layout` logs position, count, iomode, layout stateid, lseg pointer, and a symbolic reason such as no pNFS, found cached, layoutreturn, retrying, or sent layoutget.

MDS fallback events share `pnfs_layout_event`:
- `pnfs_mds_fallback_pg_init_read`
- `pnfs_mds_fallback_pg_init_write`
- `pnfs_mds_fallback_pg_get_mirror_count`
- `pnfs_mds_fallback_read_done`
- `pnfs_mds_fallback_write_done`
- `pnfs_mds_fallback_read_pagelist`
- `pnfs_mds_fallback_write_pagelist`

These are exported by `nfs4trace.c`.

## pNFS Device and Layout Driver Events

Device events:
- `nfs4_deviceid_free`
- `nfs4_getdeviceinfo`
- `nfs4_find_deviceid`
- `fl_getdevinfo`

They log deviceid bytes, server/device information, and data-server address strings.

Flexfiles events:
- `ff_layout_read_error`
- `ff_layout_write_error`
- `ff_layout_commit_error`

They log DS address, NFS status from the data server, local error, file identity, offset/count, and stateid where applicable.

Block layout events:
- `bl_ext_tree_prepare_commit`
- `bl_pr_key_reg`
- `bl_pr_key_unreg`
- `bl_pr_key_reg_err`
- `bl_pr_key_unreg_err`

These trace extent-tree commit preparation and persistent reservation key registration/unregistration status.

## NFSv4.2 Conditional Events

Under `CONFIG_NFS_V4_2`, the header defines tracepoints for newer protocol operations:

- `nfs4_llseek`: SEEK data/hole, request/result offsets, EOF flag, stateid.
- `nfs4_fallocate`
- `nfs4_deallocate`
- `nfs4_copy`: COPY, including source/destination file IDs, stateids, offsets, length, sync, intra/inter-server indication, callback/result stateid, result count and consistency flags.
- `nfs4_clone`: CLONE with source/destination file IDs, offsets, length, and stateids.
- `nfs4_copy_notify`: COPY_NOTIFY source and result stateids.
- `nfs4_offload_cancel`
- `nfs4_offload_status`
- `nfs4_getxattr`
- `nfs4_setxattr`
- `nfs4_removexattr`
- `nfs4_listxattr`

## Cross-File Relationships

- Instantiated by `nfs4trace.c`.
- `nfs4state.c` uses `trace_nfs4_state_mgr`, `trace_nfs4_state_mgr_failed`, and `trace_nfs4_state_lock_reclaim`.
- pNFS/flexfiles/block layout modules can use exported tracepoints from `nfs4trace.c`.
- `nfs4super.c` module lifetime indirectly controls these tracepoints as part of NFSv4 client support.

## Research Takeaways

`nfs4trace.h` is a comprehensive observability map for the NFSv4 client. It does not implement protocol behavior; instead it standardizes diagnostic payloads for nearly every major NFSv4 client path. Its event classes reduce duplication while keeping trace output rich enough to correlate server errors, client state bits, stateids, file identities, session slots, pNFS layout state, and NFSv4.2 copy/sparse/xattr operations.
