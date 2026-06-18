# File Research: sources/os/linux/linux-stable/fs/nfs/filelayout/filelayout.c

## Role

`filelayout.c` is the pNFS NFSv4.1 file-layout driver. It decodes layout segments, validates device IDs, selects data servers and filehandles for striped I/O, issues read/write/commit RPCs to data servers, handles data-server/session/layout failures, manages pNFS commit buckets, and registers the layoutdriver with the generic pNFS client.

## Layout offsets and striping

`filelayout_get_dserver_offset()` maps logical file offsets to data-server offsets. Sparse striping keeps the original offset. Dense striping removes holes for other data servers by using `filelayout_get_dense_offset()`, which calculates stripe number and offset within a stripe unit after subtracting `pattern_offset`.

`filelayout_pg_test()` extends generic pNFS request coalescing. For unstriped layouts it accepts the generic size. For striped layouts it prevents a pageio segment from crossing stripe-unit boundaries by comparing stripe numbers and limiting returned bytes to the remainder of the current stripe.

## Data-server RPC setup

`filelayout_read_pagelist()` and `filelayout_write_pagelist()` calculate the stripe index `j`, data-server index, connect/prepare the selected data server through `nfs4_fl_prepare_ds()`, find or create an RPC client, select the data-server filehandle, adjust offsets for dense layouts, set `hdr->ds_clp` and commit index, and initiate asynchronous pgio to the data server with filelayout-specific RPC call ops.

Read and write prepare callbacks check for bad open contexts, reset to MDS if the deviceid is invalid/unavailable, set up NFSv4.1 sequence state, and install read/write stateids. Call-done callbacks let the generic MDS ops process normal completions, but if the header has been marked redo and the task succeeded they only complete the sequence.

## Error handling and fallback to MDS

`filelayout_async_handle_error()` categorizes data-server RPC failures:

- Session errors schedule session recovery.
- `DELAY` and `GRACE` delay and retry.
- Layout invalidation errors destroy the layout, wake the slot table waitqueue, and force reset to MDS.
- Connection and transport errors mark the deviceid unavailable, mark the layout for return/failure, wake waiters, and reset to MDS.
- Retryable cases clear task status and return `-EAGAIN`.

`filelayout_reset_read()` and `filelayout_reset_write()` set `NFS_IOHDR_REDO` once and call generic resend-to-MDS helpers. This is the primary safety path when data-server I/O cannot proceed.

## Layout commit and write verifiers

`filelayout_set_layoutcommit()` requests a LAYOUTCOMMIT when writes are not committed through the MDS and not already `NFS_FILE_SYNC`. For `NFS_DATA_SYNC`, it records the end offset immediately; unstable writes defer precise end-offset handling until commit.

`filelayout_write_done_cb()` handles write completion, sets layoutcommit when appropriate, clears fattr validity so DS attributes do not update the MDS inode incorrectly, and updates writeback inode state on success.

`filelayout_commit_done_cb()` handles data-server commit completion. Reset-to-MDS prepares writes for resend; retryable errors restart the call; success records layoutcommit up to the commit low-watermark.

## Layout decode and validation

`filelayout_decode_layout()` decodes the layout body from layoutget pages with an XDR stream and scratch folio. It reads deviceid, utility flags, dense/sparse type, commit-through-MDS bit, stripe unit, first stripe index, pattern offset, number of filehandles, and each filehandle. It bounds `num_fh` against the larger of supported stripe and multipath limits and rejects oversized NFS filehandles.

`filelayout_check_layout()` rejects impossible segment parameters such as `pattern_offset` after the layout range start or zero stripe unit. `filelayout_check_deviceid()` resolves the referenced deviceid, rejects unavailable/invalid deviceids, validates first stripe index and number-of-filehandle rules for dense versus sparse layouts, and atomically installs the data-server address pointer.

## Pageio and layout acquisition

`fl_pnfs_update_layout()` wraps `pnfs_update_layout()`, treating nonfatal server errors as MDS fallback and checking the deviceid before accepting the segment. Bad deviceids mark the layout for return/failure and drop the segment.

`filelayout_pg_init_read()` and `filelayout_pg_init_write()` check current layout suitability, obtain read or read/write layout segments, and reset the pageio descriptor to MDS operations when no pNFS segment is available.

`filelayout_pg_read_ops` and `filelayout_pg_write_ops` plug these init/test functions into generic pNFS pageio read/write execution and cleanup.

## Commit bucket management

The layout maintains `struct pnfs_ds_commit_info` inside `struct nfs4_filelayout`. `filelayout_setup_ds_info()` allocates a commit array sized to either the number of data servers for sparse layouts or stripe count for dense layouts. `filelayout_mark_request_commit()` sends commit-through-MDS writes to the MDS list, otherwise calculates the correct commit bucket from the page offset and layout type. `filelayout_initiate_commit()` maps commit bucket index back to data-server index, selects the correct filehandle, and starts a data-server COMMIT RPC.

`filelayout_commit_ops` delegates scanning, recovery, and clearing to generic pNFS helpers while supplying filelayout-specific setup, release, request marking, and commit initiation.

## Module registration

`filelayout_type` registers layout id `LAYOUT_NFSV4_1_FILES`, name `LAYOUT_NFSV4_1_FILES`, `PNFS_LAYOUTGET_ON_OPEN`, one-page-ish max layoutget response, layout header/segment allocators, pageio ops, data-server info lookup, pagelist read/write, deviceid alloc/free, and generic sync. Module init/exit register and unregister the layout driver, and the module alias is `nfs-layouttype4-1`.
