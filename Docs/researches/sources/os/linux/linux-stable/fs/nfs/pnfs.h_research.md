# File Research: sources/os/linux/linux-stable/fs/nfs/pnfs.h

This header defines the public pNFS client interfaces, shared data structures, flags, layout-driver callback contract, device-id cache node type, commit helper APIs, inline range helpers, and no-op fallbacks for builds without `CONFIG_NFS_V4`.

Key data structures:
- `struct nfs4_pnfs_ds_addr`: one data-server address, including socket address, address length, list node, printable remote string, netid, and transport identifier.
- `struct nfs4_pnfs_ds`: cached data-server endpoint with address list, net namespace, `nfs_client`, refcount, and connection state bit.
- `struct pnfs_layout_segment`: cached layout segment containing list nodes, layout range, refcount, sequence number, flags, and owning `pnfs_layout_hdr`.
- `struct pnfs_layout_hdr`: per-inode layout state including refcount, outstanding layoutget count, client layout-list linkage, bulk-destroy linkage, active and returned segment lists, layoutget block counter, retry timestamp, state flags, layout stateid, sequence barrier, pending return info, last-write byte for layoutcommit, layout credential, inode pointer, and RCU head.
- `struct pnfs_device` and `struct pnfs_devicelist`: GETDEVICEINFO/GETDEVICELIST containers.
- `struct nfs4_deviceid_node`: global device-id cache node keyed by layout driver, NFS client, and deviceid, with flags, unavailable timestamp, RCU head, and atomic refcount.

Major enums and flags:
- Lseg flags: `NFS_LSEG_VALID`, `NFS_LSEG_ROC`, `NFS_LSEG_LAYOUTCOMMIT`, `NFS_LSEG_LAYOUTRETURN`, and `NFS_LSEG_UNAVAILABLE`.
- Layout flags: RO/RW layoutget failure backoff, bulk recall, layoutreturn in progress/locked/requested, invalid stateid, first-layoutget serialization, inode freeing, hashed layout, and drain.
- Driver policy flags: layoutreturn on setattr, layoutreturn on error, read whole page, and LAYOUTGET-on-OPEN.
- Device-id flags: invalid, unavailable, and no-cache.
- `enum pnfs_try_status`: attempted, not attempted, or try again, used by layout driver read/write methods.
- `enum pnfs_layout_destroy_mode`: invalidate, bulk return, or file bulk return.

Layout-driver callback contract:
- `struct pnfs_layoutdriver_type` is the central plugin interface for pNFS layout drivers.
- Required callbacks are `alloc_lseg` and `free_lseg`; registration rejects drivers without them.
- Optional callbacks cover driver setup/teardown, layout header allocation/freeing, lseg insertion/merge, return-range narrowing, pageio read/write ops, DS commit info, sync, read/write pagelist dispatch, device-id allocation/free, layoutreturn preparation, layoutcommit preparation/cleanup, layoutstats preparation, and I/O cancellation.
- The driver also exposes layout type id, name, owning module, flags, and max LAYOUTGET response size.

Commit interfaces:
- `struct pnfs_commit_ops` lets layout drivers manage DS commit buckets: setup/release DS info, commit pagelists, mark/clear request commits, scan commit lists, and recover commit requests.
- Inline wrappers (`pnfs_commit_list`, `pnfs_mark_request_commit`, `pnfs_clear_request_commit`, `pnfs_scan_commit_lists`, `pnfs_recover_commit_reqs`) fall back cleanly when DS commit state or callbacks are absent.

Important exported APIs declared here:
- Driver management: `pnfs_register_layoutdriver`, `pnfs_unregister_layoutdriver`, `pnfs_find_layoutdriver`, `pnfs_put_layoutdriver`, `set_pnfs_layoutdriver`, `unset_pnfs_layoutdriver`.
- Layout lifecycle: `pnfs_update_layout`, `pnfs_layout_process`, `pnfs_put_lseg`, `pnfs_put_layout_hdr`, `pnfs_destroy_layout`, `pnfs_destroy_layout_final`, `pnfs_destroy_all_layouts`, `pnfs_layout_destroy_byfsid`, `pnfs_layout_destroy_byclid`.
- Recall/return/stateid: `pnfs_mark_matching_lsegs_invalid`, `pnfs_mark_matching_lsegs_return`, `pnfs_mark_layout_stateid_invalid`, `nfs4_layout_refresh_old_stateid`, `pnfs_roc`, `pnfs_roc_done`, `pnfs_roc_release`, `pnfs_wait_on_layoutreturn`, `pnfs_layoutreturn_retry_later`, `pnfs_layoutreturn_free_lsegs`.
- Page I/O: pNFS read/write pageio init, cleanup, test, readpages/writepages, resend-to-MDS helpers, and pNFS read resend.
- Layoutcommit/sync: `pnfs_set_layoutcommit`, `pnfs_cleanup_layoutcommit`, `pnfs_layoutcommit_inode`, `pnfs_generic_sync`, `pnfs_nfs_generic_sync`.
- Device-id cache and DS connection: `nfs4_find_get_deviceid`, `nfs4_delete_deviceid`, `nfs4_init_deviceid_node`, `nfs4_put_deviceid_node`, availability helpers, purge, DS add/put/connect, and multipath DS address decode.
- LAYOUTGET-on-OPEN: `pnfs_lgopen_prepare`, `pnfs_parse_lgopen`, `nfs4_lgopen_release`.

Inline helper behavior:
- `pnfs_enabled_sb()` tests whether a mount has an active layout driver.
- `pnfs_layout_is_valid()` checks whether the invalid-stateid flag is clear.
- `pnfs_get_lseg()` increments lseg refcount with a memory barrier.
- Range helpers calculate inclusive/exclusive pNFS offsets and intersection for layout ranges and NFS page requests.
- `pnfs_return_layout()` marks return requested and calls `_pnfs_return_layout()` when pNFS is enabled and the inode has a layout.
- `pnfs_sync_inode()` dispatches to the active driver’s sync callback.

Build configuration:
- Under `CONFIG_NFS_V4`, the full pNFS interface is declared.
- Without `CONFIG_NFS_V4`, the header supplies no-op inline stubs that preserve callers while disabling pNFS behavior.
- `pnfs_report_layoutstat()` is only active under `CONFIG_NFS_V4_2`; otherwise it returns zero.
