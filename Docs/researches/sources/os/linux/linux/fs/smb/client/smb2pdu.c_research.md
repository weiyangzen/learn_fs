# File Research: sources/os/linux/linux/fs/smb/client/smb2pdu.c

## Purpose

`smb2pdu.c` is the main SMB2/SMB3 PDU construction and command execution implementation for the Linux CIFS/SMB client. It builds wire requests, sends them through CIFS transport helpers, parses responses, manages replay/reconnect semantics, and handles SMB2/3 operations including negotiation, session setup, tree connect, create/open, I/O, query/set info, directory enumeration, locking, oplock/lease acknowledgements, filesystem info, and SMB3 multichannel reconnect handling.

## Main Responsibilities

- Assemble SMB2 headers and fixed command bodies with correct `StructureSize`, `TreeId`, `SessionId`, credit requests, signing flags, encryption flags, DFS flags, and replay markers.
- Negotiate dialects and SMB3.1.1 negotiate contexts for preauth integrity, encryption, compression, POSIX extensions, signing capabilities, and netname.
- Establish sessions using Kerberos or raw NTLMSSP, generate/consume security blobs, and initialize signing/encryption keys through server ops.
- Connect/disconnect trees and validate negotiated SMB3 settings.
- Build `CREATE` requests with path handling, DFS path prefixes, lease/durable/persistent-handle/POSIX/security-descriptor/timewarp/query-id/EA contexts.
- Implement synchronous and asynchronous read/write paths, including SMB Direct RDMA offload descriptors when configured.
- Parse server responses with boundary checks for create contexts, ioctl output, query info, directory entries, POSIX info, and filesystem info.
- Drive reconnect and multichannel recovery, including session/channel rebind, tcon reconnect, persistent handle reopen, channel scaling, and server interface re-query.
- Report tracing/statistics for command starts, completions, failures, credits, reconnect references, and I/O progress.

## Key Control Flow

- `smb2_hdr_assemble()` creates the common SMB2 header and selects credit requests/signing flags.
- `smb2_plain_req_init()` runs reconnect handling, allocates a small or large CIFS buffer, fills the header, and updates per-command stats.
- `SMB2_negotiate()` builds dialect lists and SMB3.1.1 negotiate contexts, sends the negotiate request, validates the selected dialect, records server capabilities and sizes, decodes security blobs, decodes negotiate contexts, and allocates AEAD crypto state if encryption is available.
- `SMB2_sess_setup()` selects Kerberos or NTLMSSP and runs a small state machine through `sess_data->func`.
- `SMB2_tcon()` converts the UNC tree path to UTF-16, sends tree connect, records share type/flags/caps/TID, initializes copy-chunk limits, and optionally validates negotiation.
- `SMB2_open_init()` builds a create request and all optional create contexts; `SMB2_open()` sends it, stores file IDs, copies open metadata, and parses create contexts.
- `SMB2_ioctl()`, `query_info()`, `SMB2_query_directory()`, `send_set_info()`, `SMB2_flush()`, `__SMB2_close()`, `smb2_lockv()`, `SMB2_oplock_break()`, and `SMB2_lease_break()` follow the common pattern: initialize request, set transform/sign/replay flags, send via `cifs_send_recv()`, validate/copy response data, update stats/traces, free buffers, and replay retry if eligible.
- `smb2_async_readv()` and `smb2_async_writev()` create requests, adjust credits, optionally register SMB Direct memory regions, send via `cifs_call_async()`, and complete in callbacks that verify signatures, update byte counters, release credits, and notify netfs.
- `smb2_reconnect_server()` selects affected sessions/tcons/channels, serializes reconnects with the primary server reconnect mutex, reconnects sessions/tcons, renegotiates I/O size, reopens persistent handles, and reschedules when needed.

## Dependencies and Integration

- Depends heavily on CIFS core objects from `cifsglob.h`: `TCP_Server_Info`, `cifs_ses`, `cifs_tcon`, `cifs_fid`, `cifs_io_subrequest`, and `cifs_search_info`.
- Uses transport functions such as `cifs_send_recv()`, `cifs_call_async()`, reconnect helpers, credit helpers, and MID handling from the CIFS client.
- Uses `smb2proto.h` prototypes and SMB2/3 wire structures from SMB common headers.
- Uses `smbdirect.h` only when `CONFIG_CIFS_SMB_DIRECT` is enabled for RDMA memory registration and buffer descriptors.
- Integrates with Linux netfs through `netfs_read_subreq_terminated()`, `cifs_write_subrequest_terminated()`, and netfs trace flags.
- Integrates with tracing through `trace.h` tracepoints and with CIFS stats counters.

## Important Data Handling

- Uses little-endian conversions for all wire fields.
- Pads paths and create contexts to SMB2-required alignment.
- Uses `check_add_overflow()` / `check_sub_overflow()` and explicit response-boundary validation in several parsers.
- Keeps request buffers and sensitive auth buffers freed or zeroed through CIFS buffer release helpers and `kfree_sensitive()`.
- Treats file IDs as opaque wire values where appropriate.
- Carries SMB3 replay via `smb2_set_replay()` and bounded replay retry helpers.

## Risk Notes

- This file is security sensitive: it constructs and parses untrusted network PDUs, manages authentication material, signing/encryption policy, and reconnect state.
- Response parsing correctness depends on offset/length validation. The file contains many guards, but any new parser should follow `smb2_validate_iov()` or the create-context overflow pattern.
- Resource ownership is split across iovec elements, CIFS small/large buffers, response buffers, and caller-owned error iovs. New code must preserve the existing free conventions.
- Reconnect and multichannel code is concurrency sensitive, using multiple locks (`srv_lock`, `ses_lock`, `chan_lock`, `session_mutex`, reconnect mutex, global session lock). Lock ordering must be preserved.
- SMB Direct offload explicitly disables signed/encrypted offload; changing that requires coordinated signing/encryption transport work.
