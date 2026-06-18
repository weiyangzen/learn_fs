# File Research: sources/os/linux/linux/fs/smb/client/trace.c

## Purpose

`trace.c` is the compilation unit that instantiates CIFS/SMB client tracepoints.

## Main Behavior

- Includes `cifsglob.h` and `cifs_spnego.h` so tracepoint definitions have required type context.
- Defines `CREATE_TRACE_POINTS` before including `trace.h`, causing tracepoint storage and definitions to be emitted exactly once.

## Integration

- Supports tracepoints used throughout the SMB client, including many calls from `smb2pdu.c` and `smb2transport.c`.
- Must remain a single-definition translation unit for the tracepoint system.

## Risk Notes

- Moving `CREATE_TRACE_POINTS` into multiple files would cause duplicate tracepoint definitions.
- Removing required includes can break tracepoint macro expansion if trace payload types become incomplete.
