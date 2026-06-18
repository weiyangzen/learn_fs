# File Research: sources/os/linux/linux/fs/nfs/nfstrace.c

## Purpose

`nfstrace.c` is the tracepoint instantiation unit for generic NFS client trace events. It defines `CREATE_TRACE_POINTS` before including `nfstrace.h`, causing the trace declarations in that header to generate storage and registration code exactly once.

## Behavior

The file includes core NFS and path lookup headers, includes `internal.h`, then materializes tracepoints from `nfstrace.h`.

It exports GPL tracepoint symbols for:

- `nfs_fsync_enter`
- `nfs_fsync_exit`
- `nfs_xdr_status`
- `nfs_xdr_bad_filehandle`

## Cross-File Relationships

- `nfstrace.h` contains the actual trace event definitions.
- NFS source files include `nfstrace.h` to emit these events.
- Other GPL-compatible NFS-related modules can reference the exported tracepoint symbols.

## Research Notes

There is no runtime filesystem logic here beyond tracepoint materialization and symbol export. Its importance is build/linkage: exactly one C file must instantiate the generic NFS tracepoints.
