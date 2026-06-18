# File Research: sources/os/linux/linux/fs/nfs/nfstrace.h

## Purpose
`nfstrace.h` defines the Linux tracepoint surface for the NFS client. It is a trace-event declaration header, not an algorithm implementation file. Its role is to expose structured observability for NFS inode state, directory operations, page-cache I/O, pgio RPCs, direct I/O, mount parsing, localio, and XDR status failures.

## Main Trace Areas
- Defines `TRACE_SYSTEM nfs` and includes trace helpers from `trace/misc/fs.h`, `trace/misc/nfs.h`, and `trace/misc/sunrpc.h`.
- Provides display helpers for NFS inode cache-validity bits, NFS inode flags, writeback request flags, direct request flags, stable-write modes, verifier values, file types, open flags, lookup flags, and IOCB flags.
- Defines reusable trace event classes for common record layouts:
  - `nfs_inode_event` and `nfs_inode_event_done`
  - `nfs_update_size_class`
  - `nfs_inode_range_event`
  - `nfs_readdir_event`
  - `nfs_lookup_event` and `nfs_lookup_event_done`
  - `nfs_directory_event` and `nfs_directory_event_done`
  - `nfs_folio_event` and `nfs_folio_event_done`
  - `nfs_kiocb_event`
  - `nfs_page_class` and `nfs_page_error_class`
  - `nfs_direct_req_class`
  - `nfs_xdr_event`

## Covered Operations
- Inode/cache lifecycle: stale marking, refresh, revalidate, mapping invalidation, getattr/setattr, writeback, fsync, access, cache invalidation, readdir cache completion.
- Size/range changes: truncate, truncate-folio, WCC size update, grow/update, and readdir cache range invalidation.
- Directory/name operations: lookup, lookup revalidation, readdir lookup, atomic open, create, mknod, mkdir, rmdir, remove, unlink, symlink, hard link, rename, async rename completion, and sillyrename unlink.
- Page-cache and buffered I/O: readpage, readahead, writeback, folio reclaim, invalidate/launder, update/write begin/write end/writepages, file read/write entry tracepoints.
- RPC pgio/commit operations: initiate/read done/read short/pgio error/initiate write/writeback done/write setup/do writepage/write/commit errors/initiate commit/commit done.
- Direct I/O: direct write completion, commit completion, reschedule paths, write scheduling, and request flags.
- Optional localio: direct read/write/misaligned events when `CONFIG_NFS_LOCALIO` is enabled.
- Mount/local/XDR diagnostics: mount option assignment/parsing/path events, local filehandle open, XDR status, and bad-filehandle events.

## Integration Points
- Used by NFS client source files via `trace_nfs_*` calls.
- Depends on NFS core types such as `struct nfs_inode`, `struct nfs_page`, `struct nfs_pgio_header`, `struct nfs_commit_data`, `struct nfs_direct_req`, `struct nfs_unlinkdata`, and RPC/XDR types.
- Ends with `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE nfstrace`, and `<trace/define_trace.h>`, following kernel tracepoint header conventions.

## Invariants and Risks
- Trace fast assignments dereference NFS-specific fields and assume call sites pass valid objects with stable lifetime for the tracepoint invocation.
- Error fields are sometimes normalized as positive NFS status codes for display and sometimes stored directly; consumers must read each event format rather than assume one convention.
- This file has no direct unit-test surface. Validation is mostly compile-time tracepoint generation plus runtime tracing via ftrace/perf/tracefs.
