# File Research: sources/os/linux/linux-stable/fs/nfs/nfstrace.h

This header defines the Linux tracepoint surface for the NFS client under `TRACE_SYSTEM nfs`. It is instrumentation-only code: it declares event classes, concrete trace events, and formatting helpers used by the NFS client and pNFS paths to expose inode state, directory operations, page-cache I/O, RPC I/O, mount parsing, local I/O, and XDR decode errors.

Key trace formatting helpers:
- `nfs_show_cache_validity()` renders `NFS_INO_INVALID_*`, revalidation, deferred invalidation, and metadata invalidation bits.
- `nfs_show_nfsi_flags()` renders selected `nfs_inode` flags such as stale, invalidating, layoutcommit, layoutstats, and odirect.
- `nfs_show_wb_flags()` renders `struct nfs_page` writeback/request flags such as busy, mapped, folio, clean, commit-to-DS, teardown, unlock, uptodate, removal, and contention bits.
- `nfs_show_direct_req_flags()` renders direct I/O state bits.

Major event families:
- Inode state events: `nfs_set_inode_stale`, refresh/revalidate/invalidate/getattr/setattr/writeback/fsync enter/exit, access enter/exit, cache invalidation, and readdir cache fill/uncached completion. These capture device, fileid, filehandle hash, inode version, file type, size, NFS inode flags, cache validity, access masks, and status.
- Size and range events: `nfs_size_truncate`, `nfs_size_truncate_folio`, `nfs_size_wcc`, `nfs_size_update`, `nfs_size_grow`, and `nfs_readdir_invalidate_cache_range`.
- Directory and dentry events: lookup, lookup revalidate, readdir lookup, atomic open, create, mknod, mkdir, rmdir, remove, unlink, symlink, link, rename, async rename, and sillyrename unlink. These track parent directory fileids, names, lookup/open flags, file modes, and errors.
- Folio/page-cache events: readpage, writeback folio, invalidate/launder folio, update request, update folio, write begin/end, writepages, file read/write `kiocb`, and readahead.
- RPC page I/O events: `nfs_initiate_read`, `nfs_readpage_done`, `nfs_readpage_short`, `nfs_pgio_error`, `nfs_initiate_write`, `nfs_writeback_done`, `nfs_initiate_commit`, and `nfs_commit_done`. These record offsets, byte counts, server result counts, EOF, stability mode, write verifier, and task status.
- Request-level events: `nfs_writepage_setup`, `nfs_do_writepage`, plus write/comp/commit error events for `struct nfs_page`.
- Direct I/O events: direct commit completion, rescheduling, write completion, iovec scheduling, and write reschedule.
- Conditional local I/O events under `CONFIG_NFS_LOCALIO`: local DIO read/write/misaligned events and local filehandle open.
- Mount parsing events: mount option assignment, option presence, and mount path.
- XDR events: `nfs_xdr_status` and `nfs_xdr_bad_filehandle`, carrying SUNRPC task identifiers, XID, program/procedure names, protocol version, and decoded status.

Important implementation details:
- Event payloads usually include stable identifiers: superblock device major/minor, NFS fileid, and a hashed filehandle via `nfs_fhandle_hash()`.
- Error fields are normalized inconsistently by event family: many store positive errno-like NFS status and print negative values; some directly store `task->tk_status` or `error`. Consumers should read each `TP_fast_assign` before interpreting signs.
- The header relies on external pretty-printers from `trace/misc/fs.h`, `trace/misc/nfs.h`, and `trace/misc/sunrpc.h`.
- The final `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `#include <trace/define_trace.h>` block is intentionally outside the include guard, matching Linux tracepoint generation requirements.

Role in the grouped files:
- `pagelist.c`, `pnfs.c`, `pnfs_dev.c`, and `pnfs_nfs.c` use companion tracepoints from this header or `nfs4trace.h` to expose request coalescing, pNFS layout/device handling, commit, and fallback behavior.
