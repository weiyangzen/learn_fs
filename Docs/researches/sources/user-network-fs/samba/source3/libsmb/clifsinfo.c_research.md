# sources/user-network-fs/samba/source3/libsmb/clifsinfo.c

## Purpose

This file implements SMB client filesystem-information helpers for Unix extensions, filesystem attributes, volume and size information, POSIX filesystem statistics, and POSIX identity discovery. The SMB1 path is built on Trans2 `QFSINFO`/`SETFSINFO`; selected calls dispatch to SMB2 helpers when `smbXcli_conn_protocol(cli->conn) >= PROTOCOL_SMB2_02`.

## Important APIs, Types, and Functions

Important exported APIs are `cli_unix_extensions_version[_send/_recv]`, `cli_set_unix_extensions_capabilities[_send/_recv]`, `cli_get_fs_attr_info[_send/_recv]`, `cli_get_fs_volume_info`, `cli_get_fs_full_size_info`, `cli_get_posix_fs_info[_send/_recv]`, and `cli_posix_whoami[_send/_recv]`. Per-call state structs keep Trans2 setup/parameter buffers and parsed response fields. `cli_unix_extensions_version_recv()` updates `cli->server_posix_capabilities`; the set-capabilities completion updates `cli->requested_posix_capabilities` only after a successful server reply.

## Control Flow

Async send functions allocate a `tevent_req`, fill SMB1 setup/parameter/data buffers with `SSVAL`/`SIVAL`, call `cli_trans_send()`, and parse replies in callbacks. Synchronous wrappers reject use while other async calls are active, create a temporary event context, poll the request, then call the recv side. SMB2-specific filesystem attribute, volume, full-size, and POSIX filesystem info calls route to `cli_smb2_*` helpers instead of SMB1 Trans2. `cli_posix_whoami_done()` parses guest status, uid/gid, supplementary gids, and NDR-encoded SIDs from a bounded Trans2 response.

## State and Persistence Behavior

The file has no durable storage of its own. Persistent effects are limited to server state changed by `SMB_SET_CIFS_UNIX_INFO` and in-memory capability fields on `cli_state`. Returned arrays for POSIX gids/SIDs are talloc-owned and moved to the caller in recv functions. Response buffers are transient and freed after parsing.

## Dependencies and Integration Points

The file depends on `cli_trans`, SMB2 fnum helpers, tevent NTSTATUS helpers, Trans2 constants, gensec/credentials headers, and NDR security SID parsing. It feeds higher-level client logic that needs dialect capabilities, Unix extension negotiation, statfs-like data, quota-sized volume information, and POSIX identity mapping.

## Risks and Test Signals

Parsing risk is concentrated in server-controlled lengths: volume-name byte counts, 64-bit POSIX fields, whoami gid/SID counts, and residual bytes after SID decoding. Tests should cover SMB1 and SMB2 dialects, malformed short responses, oversized whoami counts, unknown SID encodings, capability field updates only on success, and sync wrapper rejection when async calls are outstanding.
