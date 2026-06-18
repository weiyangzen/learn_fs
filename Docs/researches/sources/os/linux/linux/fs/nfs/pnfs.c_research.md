# File Research: sources/os/linux/linux/fs/nfs/pnfs.c

## Purpose
`pnfs.c` is the central pNFS client coordinator. It registers and selects pNFS layout drivers, manages layout headers and layout segments, performs `LAYOUTGET`, handles recalls and returns, routes read/write pgio to data servers through layout drivers, falls back to MDS I/O, manages layoutcommit, handles reboot recovery, and reports layout statistics.

## Layout Driver Registration and Selection
- Maintains `pnfs_modules_tbl` under `pnfs_spinlock`.
- `pnfs_register_layoutdriver()` and `pnfs_unregister_layoutdriver()` manage layout-driver modules.
- `set_pnfs_layoutdriver()` sorts server-advertised layout types by built-in preference and attempts to find or autoload a matching layout driver.
- Supported preference order is SCSI, block volume, OSD2 objects, flex files, and NFSv4.1 files.
- `unset_pnfs_layoutdriver()` calls driver cleanup, decrements MDS count, purges deviceid cache when needed, and releases the module.

## Layout Header and Segment Lifetime
- Layout headers are allocated by the active layout driver and attached to `NFS_I(inode)->layout`.
- `pnfs_put_layout_hdr()` coordinates final detach, layoutreturn-before-free behavior, inode-freeing wakeups, and driver-specific header freeing.
- Layout segments carry ranges, iomode, seqid, refcount, validity bits, layoutcommit bits, layoutreturn bits, and return-on-close state.
- `pnfs_put_lseg()` removes invalid/unused segments, may cache them for later layoutreturn, and frees them through the layout driver.
- `pnfs_generic_layout_insert_lseg()` inserts valid segments sorted by range, with driver hooks available for custom merging/insertion.

## Stateid and Recall Handling
- Tracks layout stateid validity with `NFS_LAYOUT_INVALID_STID`.
- Maintains a sequence barrier (`plh_barrier`) to reject stale layoutget/layoutreturn replies.
- `nfs4_layout_refresh_old_stateid()` handles `NFS4ERR_OLD_STATEID` by updating or bumping stateid sequence use.
- `pnfs_mark_layout_stateid_invalid()` invalidates layout state, clears layoutcommit, drains outstanding layoutgets, and marks/free matching segments.
- `pnfs_mark_matching_lsegs_invalid()` and `pnfs_mark_matching_lsegs_return()` implement recall-range matching, segment invalidation, return marking, and in-flight I/O cancellation via driver hooks.

## LAYOUTGET Flow
- `pnfs_update_layout()` is the main layout acquisition path for read/write I/O.
- It skips pNFS when disabled, when MDS threshold hints say to use MDS, when open stateid is invalid, during bulk recall, or while failed-layout retry windows are active.
- It serializes first layoutget per file with `NFS_LAYOUT_FIRST_LAYOUTGET`, waits on layoutreturn/drain when necessary, and checks the existing segment cache first.
- When needed, it allocates `struct nfs4_layoutget`, page buffers sized to server/session limits, aligns the requested range to page boundaries, calls `nfs4_proc_layoutget()`, and processes the returned segment through `pnfs_layout_process()`.
- `pnfs_layout_process()` validates returned ranges, asks the layout driver to decode/allocate an lseg, updates layout stateid, inserts the segment, and handles return-on-close flags.

## LAYOUTGET-on-OPEN
- `pnfs_lgopen_prepare()` optionally attaches layoutget arguments to an OPEN compound when the layout driver advertises `PNFS_LAYOUTGET_ON_OPEN` and the server supports `NFS_CAP_LGOPEN`.
- Attached and floating layoutget preparations differ based on whether open state already exists.
- `pnfs_parse_lgopen()` consumes the layoutget result, disables `NFS_CAP_LGOPEN` on known unsupported errors, and inserts successful segments.
- `nfs4_lgopen_release()` releases outstanding first-layoutget state and layoutget storage.

## Layout Return and Return-on-Close
- `_pnfs_return_layout()` commits/marks all segments for return, optionally asks the driver to adjust return range, sends `LAYOUTRETURN`, waits for completion, and frees returned lsegs.
- `pnfs_commit_and_return_layout()` blocks new layoutgets, waits for dirty data, performs layoutcommit, then returns layout.
- `pnfs_layoutreturn_before_put_layout_hdr()` can trigger async layoutreturn when the final header put sees pending return state.
- `pnfs_roc()` implements return-on-close compounding when no conflicting open state/delegation remains, with `pnfs_roc_done()` and `pnfs_roc_release()` handling retry, release, stateid update, and error cases.
- `pnfs_wait_on_layoutreturn()` lets RPC tasks sleep while layoutreturn is in progress.

## Bulk Recall, Destroy, and Reboot Recovery
- `pnfs_destroy_layout()` and `pnfs_destroy_layout_final()` invalidate and eventually detach an inode layout.
- Bulk destroy helpers build per-client/per-fsid lists of layout headers using RCU and superblock activity protection.
- `pnfs_layout_destroy_byfsid()` and `pnfs_layout_destroy_byclid()` invalidate or return layouts in bulk.
- `pnfs_destroy_all_layouts()` invalidates deviceids, purges deviceid cache, and destroys client layouts after lease expiry.
- `pnfs_layout_handle_reboot()` builds a recover list, attempts privileged reboot layoutreturns where supported, then invalidates remaining layouts.

## pNFS Read/Write Routing
- `pnfs_generic_pg_init_read()` and `pnfs_generic_pg_init_write()` select or acquire a matching layout segment for a pageio descriptor.
- If no segment is available, the descriptor is reset to normal MDS read/write.
- `pnfs_generic_pg_test()` wraps generic coalescing with layout-segment boundary checks.
- `pnfs_generic_pg_readpages()` and `pnfs_generic_pg_writepages()` allocate pgio headers, attach layout segment refs, build generic pgio data, and dispatch through the layout driver.
- Layout-driver read/write outcomes:
  - `PNFS_ATTEMPTED`: driver owns completion.
  - `PNFS_NOT_ATTEMPTED`: retry through MDS.
  - `PNFS_TRY_AGAIN`: recoalesce and retry pNFS.
- `pnfs_ld_read_done()` and `pnfs_ld_write_done()` are completion helpers for non-RPC layout drivers.
- On data-server errors, optional `PNFS_LAYOUTRET_ON_ERROR` returns the layout, and failed I/O is resent to MDS.

## Layoutcommit and Sync
- `pnfs_set_layoutcommit()` marks inode and lseg layoutcommit state, records last written byte, and dirties the inode for later layoutcommit.
- `pnfs_layoutcommit_inode()` serializes layoutcommit with `NFS_INO_LAYOUTCOMMITTING`, collects RW lsegs, prepares driver-specific layoutcommit data, sends `nfs4_proc_layoutcommit()`, and redirties on failure.
- `pnfs_cleanup_layoutcommit()` calls layout-driver cleanup and releases lseg references.
- `pnfs_generic_sync()` delegates sync to layoutcommit.

## MDS Thresholds and Layoutstats
- `pnfs_within_mdsthreshold()` implements RFC threshold hints from OPEN to keep small file or small I/O on the MDS.
- `pnfs_mdsthreshold_alloc()` allocates threshold state.
- Under `CONFIG_NFS_V4_2`, `pnfs_report_layoutstat()` prepares and sends layout statistics if pNFS and server capabilities allow it.
- `layoutstats_timer` is exported as a module parameter.

## Invariants and Risks
- The inode `i_lock`, client `cl_lock`, RCU list traversal, refcounts, and bit locks form the main safety model.
- First-layoutget serialization is required by protocol errata; removing it can violate stateid sequencing.
- Layoutreturn and layoutget are serialized to avoid freeing lsegs while new layoutgets depend on old state.
- Error fallback to MDS is essential for pNFS correctness; layout drivers must honor the `PNFS_*` try-status contract.
- Layoutcommit lseg references are subtle: references taken in `pnfs_set_layoutcommit()` are released through layoutcommit cleanup paths.
