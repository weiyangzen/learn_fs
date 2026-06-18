# File Research: sources/os/linux/linux-stable/fs/nfs/nfstrace.c

## Purpose

`nfstrace.c` instantiates and exports selected NFS tracepoints.

## Contents

The file:

- Includes NFS and path lookup headers.
- Includes `internal.h`.
- Defines `CREATE_TRACE_POINTS` before including `nfstrace.h`, causing tracepoint definitions to be emitted here.
- Exports tracepoint symbols for GPL modules:
  - `nfs_fsync_enter`
  - `nfs_fsync_exit`
  - `nfs_xdr_status`
  - `nfs_xdr_bad_filehandle`

## Dependencies

Tracepoint declarations live in `nfstrace.h`. This file provides the single compilation unit that materializes those declarations as tracepoint definitions.

## Research Notes

This is a tracepoint definition/export shim. It contains no runtime logic beyond symbol creation and export.
