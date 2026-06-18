# File Research: sources/os/linux/linux/fs/nfs/flexfilelayout/flexfilelayout.c

## Purpose
Implements the NFSv4 pNFS flexfile layout driver. It decodes flexfile layout segments, manages mirrors/stripes, routes read/write/commit I/O to data servers, records layout statistics and DS errors, prepares layoutreturn/layoutstats payloads, and registers the `LAYOUT_FLEX_FILES` layout driver.

## Main Responsibilities
- Allocate/free flexfile layout headers and segments.
- Decode layout opaque data: stripe unit, mirror count, DS stripe count, device IDs, efficiency, stateids, filehandles, UID/GID-derived DS credentials, layout flags, and stats report interval.
- Reuse identical mirrors across layout segments using deviceid and filehandle comparisons.
- Sort mirrors by aggregate efficiency.
- Select data servers for reads and writes, including striped DSS selection via `nfs4_ff_layout_calc_dss_id()`.
- Initialize pageio read/write operations and coalescing boundaries so striped I/O does not cross stripe units.
- Dispatch pNFS reads, writes, and commits through DS RPC clients or localio.
- Handle DS errors and decide whether to retry pNFS, fall back to the MDS, mark a layout for return, or treat errors as fatal.
- Track and encode layoutstats and layoutreturn error reports.
- Register/unregister the flexfile layout driver module.

## Key Data Flow
`ff_layout_alloc_lseg()` decodes a layoutget response into `struct nfs4_ff_layout_segment`, containing a flexible array of mirror pointers. Each mirror owns DSS entries with device IDs, filehandles, credentials, localio state, per-DS read/write statistics, and delayed `mirror_ds` resolution.

Read setup:
- `ff_layout_pg_init_read()` obtains or refreshes a read layout.
- `ff_layout_get_ds_for_read()` chooses the best available mirror/stripe.
- `ff_layout_read_pagelist()` prepares DS connection/client/credential/filehandle/stateid and calls `nfs_initiate_pgio()`.

Write setup:
- `ff_layout_pg_get_mirror_count_write()` exposes the mirror count to pageio.
- `ff_layout_pg_init_write()` prepares every mirror needed for mirrored writes.
- `ff_layout_write_pagelist()` dispatches each mirrored write and assigns a DS commit index.

Commit setup:
- Commit index is encoded as `mirror_idx * dss_count + dss_id`.
- `ff_layout_initiate_commit()` maps the commit index back to mirror/DSS, prepares the DS client, and starts `nfs_initiate_commit()`.

## Error and Recovery Behavior
`ff_layout_io_track_ds_error()` maps local/RPC errors into NFSv4 layout error statuses, records them with `ff_layout_track_ds_error()`, marks DS device IDs unreachable for NXIO-style failures, and often marks the layout for return.

`ff_layout_async_handle_error_v3()` and `_v4()` are protocol-specific recovery engines:
- NFSv4 session errors schedule session recovery.
- Delay/grace/jukebox conditions retry after delay.
- Layout-invalidating errors destroy or return layouts.
- Connection failures delete unavailable device IDs.
- `fatal_neterrors` can convert network unreachable cases into fatal I/O.

Fallback logic distinguishes:
- `NFS_IOHDR_RESEND_PNFS` for retrying another DS/mirror.
- `NFS_IOHDR_RESEND_MDS` for MDS fallback.
- `FF_FLAGS_NO_IO_THRU_MDS` and availability checks can force continued pNFS retry behavior.

## Layoutstats and Layoutreturn
Per-DSS read/write stats track requested/completed ops/bytes, not-delivered bytes, busy time, and aggregate completion time. `nfs4_ff_layoutstat_start_io()` triggers layoutstats reporting based on mirror/server interval or global `layoutstats_timer`.

`ff_layout_prepare_layoutreturn()` gathers up to `FF_LAYOUTRETURN_MAXERR` DS errors and up to `FF_LAYOUTSTATS_MAXDEV` stat entries, encodes them into a one-page opaque payload, and frees private data through `layoutreturn_ops`.

When NFSv4.2 is enabled, `ff_layout_send_layouterror()` sends collected DS errors through `nfs42_proc_layouterror()` in bounded batches.

## Important Types and Operations
- `flexfilelayout_type`: `struct pnfs_layoutdriver_type` registration for `LAYOUT_FLEX_FILES`.
- `ff_layout_pg_read_ops`, `ff_layout_pg_write_ops`: pageio operation tables.
- `ff_layout_commit_ops`: pNFS commit operation table.
- `ff_layout_read/write/commit_call_ops_v3/v4`: DS RPC call operation tables.
- `ff_layout_prepare_layoutstats()`: prepares `LAYOUTSTATS`.
- `ff_layout_cancel_io()`: cancels matching DS RPC tasks for a returned/invalid layout segment.

## Concurrency and Lifetime Notes
- Layout header and mirror lists are protected by inode `i_lock`.
- Mirror stats use `mirror->lock`.
- Mirror references use `refcount_t`; reused mirrors swap credentials and release superseded mirrors.
- Device ID nodes use pNFS device ID refcounting and RCU freeing.
- Credentials are RCU-published per DSS and dropped on mirror free.
- Layoutstats opaque data holds a mirror reference until encode/free completes.
- DS RPC cancellation matches task call ops and calldata against the layout segment.

## Research Notes
This file is the central flexfile pNFS implementation. Changes here affect pNFS correctness, MDS fallback semantics, DS error propagation, mirrored write consistency, layoutreturn behavior, and NFSv4.2 layoutstats/layout error reporting.
