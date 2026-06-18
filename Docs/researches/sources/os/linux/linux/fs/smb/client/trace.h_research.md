# File Research: sources/os/linux/linux/fs/smb/client/trace.h

## Scope
Read completely: 1,968 lines. This header defines the CIFS/SMB client tracepoint surface for ftrace/perf-style observability. It contains trace enums, enum-to-string mappings, event classes, concrete `TRACE_EVENT`/`DEFINE_EVENT` instances, and the final `trace/define_trace.h` inclusion.

## Purpose
`trace.h` is the central tracepoint declaration file for the SMB client. It exposes structured diagnostics for I/O, copy offload, file handle operations, locks, query/set info, compounds, command status, MID lifecycle, tree connect, opens, leases, connection setup, session setup, reconnects, ioctls, shutdown, credit accounting, Kerberos upcalls, tcon refcounts, read/write credit accounting, and generic EIO classification.

## Main Trace Domains
- EIO classification: `smb_eio_traces` enumerates many validation and protocol failure labels used by `smb_EIO*()` helpers throughout the client.
- Read/write credits: `smb3_rw_credits_traces` classifies credit transitions for netfs-style read/write subrequests.
- Tcon refs: `smb3_tcon_ref_traces` classifies tree connection refcount get/put/free observations.
- I/O events: `smb3_read_*`, `smb3_write_*`, `smb3_query_dir_*`, `smb3_zero_*`, and `smb3_falloc_*`.
- Copy/clone events: `smb3_copychunk_*` and `smb3_clone_*`.
- Handle events: flush, close, oplock-not-found, lock enter/done/error/cached, and lock conflicts.
- Info and compound events: query/set info, notify, hardlink, rename, unlink, EOF, reparse, WSL EA, mkdir, tree disconnect, mknod.
- Command/MID events: command enter/done/error, session expiry, slow responses, function enter/exit, sync errors.
- Session/transport events: connect, SMB Direct connect, Kerberos auth, key expiry, reconnect, missing session.
- Admin/control events: ioctl, unsupported ioctl, shutdown, shutdown error.
- Credit events: invalid credits across reconnect, timeout, insufficient credits, add/adjust/header/nonblocking/pending/wait/overflow/set credits.

## Structure
The file follows Linux tracepoint conventions:
- Defines `TRACE_SYSTEM cifs`.
- Uses `EM`/`E_` macro lists to define enums once, export enum values with `TRACE_DEFINE_ENUM`, and generate symbolic print mappings.
- Uses `DECLARE_EVENT_CLASS` for repeated payload shapes and small `DEFINE_*` wrappers for concrete event names.
- Uses direct `TRACE_EVENT` for bespoke payloads such as lock conflicts, cached opens/closes, Kerberos auth, tcon refs, read/write credits, and EIO labels.
- Ends with `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE trace`, and `#include <trace/define_trace.h>`.

## Key Payload Patterns
Trace records consistently include SMB identifiers:
- `xid` for client transaction tracking.
- `sesid`, `tid`, and `fid` for SMB session/tree/file handle identity.
- `mid`, `cmd`, and `status` for SMB2 command response flow.
- offsets and lengths for I/O, zeroing, copy, clone, and locks.
- `conn_id`, `hostname`, socket address, and current MID for connection and credit traces.
- lease keys, lease state, flags, and epoch for lease break/ack paths.

## Integration Points
This file is included indirectly by SMB client C files that emit tracepoints. It is tightly coupled to:
- `transport.c` for send, reconnect, MID, credit, and read receive errors.
- `smb2ops.c` for SMB2/3 credits, copychunk, clone, leases, encryption receive, and compound paths.
- `inode.c`, `link.c`, `reparse.c`, `ioctl.c`, and `xattr.c` through EIO labels and operation-specific trace events.
- CIFS stats and debugging paths that use slow-response and credit tracepoints.

## Notable Behaviors
- EIO labels make otherwise generic `-EIO` failures distinguishable by protocol validation site.
- Kerberos auth trace includes pid, uid, cruid, host, user, address, selected security flavor, upcall target, and rc.
- `smb3_rw_credits` traces carry both request/subrequest ids and server credit pool state.
- `smb3_tcon_ref` traces expose refcount lifecycle events for diagnosing mount/session/tcon lifetime bugs.
- The copy-range trace print format stores both source and target FIDs, but the `TP_printk` arguments print `target_fid` in the source-FID field as well. This affects trace readability, not protocol behavior.

## Risks And Review Focus
- Tracepoint payload layouts are a userspace ABI-like observability surface; changes can break tracing scripts.
- Event classes must keep types aligned with call sites, especially for FIDs and endianness-neutral values.
- EIO enum additions should preserve symbolic mapping consistency through all three macro phases.
- Trace strings that include usernames, hostnames, paths, and Kerberos details can expose sensitive operational metadata when tracing is enabled.

## Research Takeaways
`trace.h` is not protocol logic, but it is critical for diagnosing the SMB client. It provides the vocabulary used to distinguish credit starvation, malformed responses, reconnect races, lease issues, failed FSCTLs, xattr/ACL validation, and encrypted/large-read receive failures.
