# File Research: sources/os/linux/linux/fs/nfs/filelayout/filelayout.c

## Role

`filelayout.c` implements the NFSv4.1 pNFS files layout driver. It registers layout type `LAYOUT_NFSV4_1_FILES`, decodes file layout segments, chooses data servers for read/write/commit I/O, handles data-server errors, maps dense/sparse striping, and manages pNFS commit buckets.

The module registers with `pnfs_register_layoutdriver()` in `nfs4filelayout_init()` and unregisters in `nfs4filelayout_exit()`.

## Layout Segment Geometry

`filelayout_get_dserver_offset()` maps a logical file offset to a data-server offset. Sparse layouts use the original offset. Dense layouts use `filelayout_get_dense_offset()`, which computes stripe number and remainder from `pattern_offset`, `stripe_unit`, and `stripe_count`.

`filelayout_pg_test()` prevents pageio coalescing across stripe boundaries. It delegates generic checks to `pnfs_generic_pg_test()` and then limits request size to the remaining bytes in the current stripe for striped layouts.

## Data-Server Read/Write Paths

`filelayout_read_pagelist()` and `filelayout_write_pagelist()` calculate the stripe index with `nfs4_fl_calc_j_index()`, map it to a DS index with `nfs4_fl_calc_ds_index()`, prepare/connect the DS via `nfs4_fl_prepare_ds()`, create/find a DS RPC client, select the appropriate filehandle with `nfs4_fl_select_ds_fh()`, adjust offsets for dense layouts, and initiate asynchronous NFS read/write RPCs through the data-server client.

`filelayout_read_prepare()` and `filelayout_write_prepare()` validate the open context, reset to MDS if the device is unavailable, set up the NFSv4.1 session sequence, and install read/write stateids. Completion callbacks route errors through `filelayout_async_handle_error()`.

## Error Handling And MDS Fallback

`filelayout_async_handle_error()` centralizes DS error handling:
- Session errors schedule session recovery.
- `NFS4ERR_DELAY`/`GRACE` delay and retry.
- Layout-invalidating errors destroy or return the layout and reset I/O to MDS.
- Connection/device errors mark the device ID unavailable, mark layout for return, set layout failure, wake slot waiters, and reset to MDS.

`filelayout_reset_read()` and `filelayout_reset_write()` set `NFS_IOHDR_REDO` and call generic pNFS resend-to-MDS helpers.

## Layout Decoding And Validation

`filelayout_decode_layout()` decodes layoutget results from XDR pages. It extracts deviceid, utility flags, commit-through-MDS flag, dense/sparse stripe type, stripe unit, first stripe index, pattern offset, filehandle count, and filehandle array. It validates filehandle sizes against `NFS_MAXFHSIZE`.

`filelayout_check_layout()` validates basic segment geometry, including `pattern_offset <= layout range offset` and nonzero stripe unit.

`filelayout_check_deviceid()` obtains the decoded deviceid node, rejects unavailable devices, validates `first_stripe_index`, and checks filehandle count rules for sparse versus dense layouts. It installs the DS address pointer with `cmpxchg()` to avoid races.

`filelayout_alloc_lseg()` allocates and decodes a layout segment. `filelayout_free_lseg()` releases the deviceid, releases per-lseg DS commit info for RW segments, and frees filehandles.

## Layout Acquisition

`fl_pnfs_update_layout()` wraps `pnfs_update_layout()`. Recoverable server errors fall back to MDS by returning `NULL`. After acquiring a segment, it validates the deviceid; invalid device metadata marks the layout for return, marks layout failure, releases the segment, and falls back.

`filelayout_pg_init_read()` and `filelayout_pg_init_write()` initialize pageio descriptors, request READ or RW layouts, and reset to MDS pageio ops when no layout is available.

## Commit Handling

Writes that are not committed through the MDS are bucketed by data server. `filelayout_mark_request_commit()` either adds the request to the MDS commit list or maps the request offset to a DS commit bucket. Sparse and dense layouts use different bucket-to-DS mappings.

`filelayout_initiate_commit()` prepares DS commit RPCs, chooses the DS client and filehandle, installs `filelayout_commit_done_cb()`, and initiates commit. Failure prepares writes for resend and releases commit data.

`filelayout_commit_done_cb()` uses the same async error path; reset-to-MDS prepares writes for resend, retry restarts the RPC, and success sets layoutcommit state.

`filelayout_commit_ops` plugs setup/release, mark/clear, scan/recover, and commit-pagelist behavior into generic pNFS commit infrastructure.

## Layout Driver Registration

`filelayout_type` declares:
- layout id `LAYOUT_NFSV4_1_FILES`,
- `PNFS_LAYOUTGET_ON_OPEN`,
- max layoutget response of 4096 bytes,
- layout header and segment alloc/free hooks,
- read/write pageio ops,
- DS commit info access,
- read/write pagelist functions,
- deviceid alloc/free hooks,
- generic sync callback.

The module alias is `nfs-layouttype4-1`.
