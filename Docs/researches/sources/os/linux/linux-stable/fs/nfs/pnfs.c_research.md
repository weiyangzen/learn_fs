# File Research: sources/os/linux/linux-stable/fs/nfs/pnfs.c

This file is the main pNFS client layout manager. It selects and registers layout drivers, manages per-inode layout headers and layout segments, performs LAYOUTGET/LAYOUTRETURN/LAYOUTCOMMIT orchestration, routes page I/O to data servers or back to the metadata server, handles recalls/reboots/old stateids, and reports optional layout statistics.

Driver management:
- `pnfs_register_layoutdriver()` and `pnfs_unregister_layoutdriver()` maintain the global `pnfs_modules_tbl` protected by `pnfs_spinlock`.
- `set_pnfs_layoutdriver()` sorts server-advertised layout types by local preference (`SCSI`, block volume, OSD2, flex files, NFSv4.1 files), requests missing modules, selects one driver per filesystem, calls its `set_layoutdriver()`, and increments the client MDS count.
- `unset_pnfs_layoutdriver()` calls driver cleanup, decrements MDS count, purges device IDs when the last MDS reference drops, and releases the module.

Layout header and segment lifecycle:
- `pnfs_layout_hdr` is allocated through the active driver and attached to `NFS_I(inode)->layout`.
- `pnfs_put_layout_hdr()` runs deferred layoutreturn checks, detaches the header when the refcount drops to zero, wakes inode teardown waiters, and frees through the driver.
- `pnfs_layout_segment` objects are initialized with ranges, stateid sequence numbers, flags, refcounts, and backpointers.
- `pnfs_put_lseg()` removes an lseg when its refcount drops to zero, optionally caching it on `plh_return_segs` if it must be returned to the server.
- `pnfs_mark_matching_lsegs_invalid()` invalidates matching lsegs for recalls or stateid loss and cancels driver I/O for still-busy segments.
- `pnfs_mark_matching_lsegs_return()` marks matching lsegs for LAYOUTRETURN, returning `0` when a return should be scheduled, `-EBUSY` when live references remain, and `-ENOENT` when nothing matches.

Stateid and sequencing:
- `pnfs_seqid_is_newer()` handles wraparound-aware layout stateid sequence comparisons.
- `plh_barrier` blocks stale layoutget/layoutreturn stateids.
- `pnfs_set_layout_stateid()` installs a new layout stateid, updates credentials, clears invalid-state flags, updates the barrier, and resets return state when appropriate.
- `nfs4_layout_refresh_old_stateid()` handles `NFS4ERR_OLD_STATEID` by either bumping the caller’s stateid or forcing matching lsegs to be returned and copying the current seqid.

LAYOUTGET path:
- `pnfs_update_layout()` is the central lookup/acquire path. It checks pNFS availability, MDS threshold hints, valid open state, expired lease recovery, bulk recall, previous layoutget failure backoff, layout drain, layoutreturn waits, and cached segment lookup.
- If no usable segment exists, it serializes first layoutget after an invalid layout stateid, selects the open stateid or current layout stateid, blocks if layoutgets are disabled, aligns the requested range to page boundaries, allocates `nfs4_layoutget`, and calls `nfs4_proc_layoutget()`.
- `pnfs_layout_process()` validates the server-returned range, asks the layout driver to decode/allocate an lseg, checks blocked/draining/stale stateid conditions, updates layout stateid, inserts the segment, and records return-on-close when requested.
- `pnfs_lgopen_prepare()`, `pnfs_parse_lgopen()`, and `nfs4_lgopen_release()` support optional LAYOUTGET-on-OPEN compounds.

LAYOUTRETURN and recall handling:
- `_pnfs_return_layout()` commits/clears layoutcommit state, marks all lsegs for return, lets the driver narrow the return range, sends LAYOUTRETURN when valid segments exist, and waits for completion.
- `pnfs_commit_and_return_layout()` blocks new layoutgets and data-server I/O, waits for writeback, sends LAYOUTCOMMIT, then returns the layout.
- `pnfs_layoutreturn_retry_later()` and `pnfs_layoutreturn_free_lsegs()` update local state after failed or completed layoutreturns.
- `pnfs_layoutreturn_before_put_layout_hdr()` opportunistically sends asynchronous LAYOUTRETURN when all needed segment references have drained.
- `pnfs_roc()`, `pnfs_roc_done()`, and `pnfs_roc_release()` implement return-on-close, including optional compound layoutreturn, credential matching, retry/error handling, and segment freeing.
- Bulk destroy helpers handle recalls by fsid, clientid, expired lease, and server reboot. Reboot support uses privileged LAYOUTRETURN with the zero stateid when the server advertises reboot layoutreturn capability.

I/O routing:
- `pnfs_generic_pg_init_read()` and `pnfs_generic_pg_init_write()` attach a suitable layout segment to the pageio descriptor by calling `pnfs_update_layout()`, falling back to MDS read/write if no segment is available.
- `pnfs_generic_pg_test()` wraps `nfs_generic_pg_test()` and further limits coalescing to the current layout segment boundary.
- `pnfs_generic_pg_readpages()` and `pnfs_generic_pg_writepages()` allocate pgio headers, attach a referenced lseg, build generic pgio payloads, then call driver `read_pagelist()` or `write_pagelist()`.
- If a driver returns `PNFS_NOT_ATTEMPTED`, reads/writes are requeued through the MDS path. If it returns `PNFS_TRY_AGAIN`, pages are restored to the descriptor and recoalesced.
- `pnfs_ld_read_done()` and `pnfs_ld_write_done()` are completion entry points for non-RPC-based layout drivers; they call MDS completion ops on success and resend through MDS on pNFS errors.
- `pnfs_read_resend_pnfs()` resends read pages through pNFS after dropping the header lseg to avoid layoutreturn deadlocks.

LAYOUTCOMMIT and sync:
- `pnfs_set_layoutcommit()` marks the inode and segment as needing layoutcommit, records the highest last-write byte, takes an lseg reference, and marks the inode dirty.
- `pnfs_layoutcommit_inode()` serializes layoutcommit with `NFS_INO_LAYOUTCOMMITTING`, prepares driver-private layoutcommit data, sends `nfs4_proc_layoutcommit()`, and re-dirties the inode on failure.
- `pnfs_cleanup_layoutcommit()` calls driver cleanup and releases lseg references collected for the layoutcommit.
- `pnfs_generic_sync()` maps sync to a synchronous layoutcommit.

Other behavior:
- MDS threshold logic in `pnfs_within_mdsthreshold()` honors OPEN-returned read/write file-size and cumulative-I/O thresholds to keep small files or small I/O on the MDS.
- `pnfs_layout_return_unused_byclid()` scans cached layouts and asynchronously returns layouts with no matching open mode.
- `pnfs_report_layoutstat()` conditionally reports NFSv4.2 layout stats if enabled and supported.
- `layoutstats_timer` is a module parameter exported for layout statistics scheduling.

Concurrency:
- `inode->i_lock` protects each inode’s layout pointer, layout flags, segment lists, return lists, and layout stateid.
- `cl_lock` and RCU protect client/server layout lists used for recalls and bulk destruction.
- Atomic `plh_outstanding` tracks in-flight layoutget operations and coordinates drain.
- Bit locks serialize first LAYOUTGET, LAYOUTRETURN, and LAYOUTCOMMITTING waiters.
- Segment and header refcounts prevent freeing while I/O, commit, return, or bulk-destroy paths still hold references.
