# File Research: sources/os/linux/linux-stable/fs/smb/client/trace.h

## Summary
Defines the Linux CIFS/SMB client tracepoint surface for ftrace/perf diagnostics. It declares symbolic trace enums for SMB EIO reasons, read/write credit transitions, and tree-connect reference transitions, then builds reusable `DECLARE_EVENT_CLASS` templates and concrete `TRACE_EVENT`/`DEFINE_EVENT` instances for the SMB client’s main runtime paths.

## Main Responsibilities
- Export symbolic trace enums for wire-parse errors, malformed response reasons, credit accounting transitions, and tcon reference lifecycle events.
- Trace read/write enter/done/error paths with request debug IDs, FIDs, TIDs, session IDs, offsets, lengths, and return codes.
- Trace copy-range, clone, zero-range, fallocate, query-dir, EOF, flush, close, lock, ioctl, shutdown, open, cached-open, cached-close, lease, reconnect, session, tree-connect, and query/set-info paths.
- Trace connection establishment and SMB Direct connection status with hostname, connection ID, destination socket address, and errors.
- Trace credit wait/add/adjust/timeout/overflow cases with current MID, server, credit pool, delta, and in-flight count.
- Trace Kerberos/SPNEGO auth metadata, tcon refs, read/write subrequest credit state, and compact `smb3_eio` symbolic failure records.

## Key Interfaces
- Enum sets: `smb_eio_traces`, `smb3_rw_credits_traces`, `smb3_tcon_ref_traces`.
- Exported enums: `enum smb_eio_trace`, `enum smb3_rw_credits_trace`, `enum smb3_tcon_ref_trace`.
- Important event families: `smb3_read_*`, `smb3_write_*`, `smb3_copychunk_*`, `smb3_clone_*`, `smb3_query_info_*`, `smb3_set_info_*`, `smb3_open_*`, `smb3_lease_*`, `smb3_connect_*`, `smb3_reconnect`, `smb3_*_credits`, `smb3_kerberos_auth`, `smb3_tcon_ref`, `smb3_rw_credits`, and `smb3_eio`.

## Integration Notes
This header is included by SMB client C files that emit `trace_smb3_*`, `trace_cifs_*`, and `trace_smb3_eio` calls. The final `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `<trace/define_trace.h>` inclusion make it the provider for tracepoint definitions when compiled in the trace-defining translation unit.

## Risks
The file is declarative but high leverage: trace field order and `TP_PROTO`/`TP_ARGS` signatures must stay synchronized with all call sites. Symbolic enum edits can affect user-space trace decoding. Some trace classes carry paths, usernames, hostnames, socket addresses, FIDs, and security/auth context, so diagnostic usefulness must be balanced against data exposure in trace logs.
