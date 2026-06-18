# File Research: sources/os/linux/linux/fs/xfs/scrub/trace.h

This is the tracepoint catalog for XFS online scrub and repair. It defines ftrace event classes, symbolic strings, and concrete trace events for scrub dispatch, errors, btree traversal, xfile/xfarray operations, inode scans, link/count repair, directory tree repair, temporary files, symlink repair, and realtime repair. The header explicitly states these tracepoints are not stable kernel ABI.

Top-level definitions:
- `TRACE_SYSTEM xfs_scrub`
- Forward declarations for scrub, xfile, xfarray, quota iterator, inode scan, nlink, fscounters, rmap updates, parent records, and dirtree state.
- `TRACE_DEFINE_ENUM` entries for scrub types, refcount domains, group types, rmap ops, dirtree outcomes, and other symbolic values.
- String tables: `XFS_SCRUB_TYPE_STRINGS`, `XFS_SCRUB_FLAG_STRINGS`, `XFS_SCRUB_STATE_STRINGS`, `XCHK_DIRPATH_OUTCOME_STRINGS`.

Major scrub trace groups:
- Scrub lifecycle: `xchk_start`, `xchk_done`, `xchk_deadlock_retry`, `xrep_attempt`, `xrep_done`.
- Fsgates: `xchk_fsgates_enable`, `xchk_fsgates_disable`.
- Vectored scrub: `xchk_scrubv_start`, `xchk_scrubv_item`, `xchk_scrubv_outcome`, `xchk_scrubv_barrier_fail`.
- General errors: op errors, file op errors, block/inode/file-block corruption, warnings, preen events, incomplete scans.
- Btree tracing: btree operation errors, btree corruption, inode-fork btree events, btree record/key events, xref errors.
- Filesystem counters and freeze/thaw events.
- Quota-specific iterator and quotacheck events under `CONFIG_XFS_QUOTA`.

xfile and xfarray events:
- `xfile_create`, `xfile_destroy`, `xfile_load`, `xfile_store`, `xfile_seek_data`, `xfile_get_folio`, `xfile_put_folio`, `xfile_discard`.
- `xfarray_create`, `xfarray_isort`, `xfarray_foliosort`, `xfarray_qsort`, `xfarray_sort`, `xfarray_sort_scan`, `xfarray_sort_stats`.

Scrub-side higher-level events:
- Realtime summary free-record tracing under `CONFIG_XFS_RT`.
- Inode scan cursor, visit, skip, batch iget, and retry-wait events.
- Nlink collection, live updates, zero-link checks, incore updates, and inode comparison.
- Parent pointer slowpath/defer tracing.
- Dirtree/path construction, upward walks, disappeared/bad-generation/nondirectory/unlinked/crossing path states, outcome setting/evaluation, live updates, and metapath lookup.

Repair trace groups under `CONFIG_XFS_ONLINE_REPAIR`:
- Reaping and extent disposal/binval limits.
- Rebuild discovery events for allocation btrees, inode btrees, refcount, bmap, rmap, and findroot.
- AG and rtgroup repair reservation sizing.
- Counter reset and new-btree allocation/claiming.
- Dinode and inode repair decisions.
- CoW repair mapping and staging-free events.
- Quota repair events.
- Nlink repair updates.
- Rmap live update events.
- Temporary file creation/preallocation/copy-in and old fork extent reaping.
- Xattr salvage/rebuild, parent pointer stash/replay, and xattr parent scans.
- Directory recovery, dirent salvage/replay, adoption, parent finding, and dentry invalidation.
- Symlink salvage target, rebuild, and reset-fork events.
- Inode unlinked-list walking, reload, resolve, relink, add, and commit events.
- Metapath repair lookup/link/unlink events.
- Realtime bitmap and realtime rmap repair events under `CONFIG_XFS_RT`.

Integration:
- Included by ordinary scrub/repair files for trace event declarations.
- Included by `trace.c` with `CREATE_TRACE_POINTS` to instantiate events.
- Ends with `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE scrub/trace`, and `<trace/define_trace.h>`.

Risk notes:
- The file is dense generated-trace infrastructure rather than normal control flow; mistakes in event field extraction can break builds or produce misleading diagnostics.
- Several events are config-gated, so consumers must account for missing events depending on kernel config.
- Trace output includes names and symlink targets in some repair paths, so it can expose filesystem metadata to privileged trace readers.
