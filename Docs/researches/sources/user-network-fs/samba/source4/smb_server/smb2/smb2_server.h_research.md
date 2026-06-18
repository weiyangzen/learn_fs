# sources/user-network-fs/samba/source4/smb_server/smb2/smb2_server.h

## Purpose
This header defines the SMB2 request context and the core macros used by source4 SMB2 command handlers. It centralizes request lifetime fields, chaining state, signing flags, inbound/outbound buffers, NTVFS request setup, body validation, error propagation, and async completion checks.

## Important APIs, Types, And Functions
The primary type is `struct smb2srv_request`, which links into connection pending lists and stores `smb_conn`, `tcon`, `session`, control flags, request time, IO pointer, NTVFS request, status, sequence number, pending id, chain metadata, chained file/session/tree data, signing state, and SMB2 input/output buffers. It includes generated `smb2_proto.h`. Macros include `SMB2SRV_CHECK_BODY_SIZE`, `SMB2SRV_CHECK`, `SMB2SRV_TALLOC_IO_PTR`, `SMB2SRV_SETUP_NTVFS_REQUEST`, `SMB2SRV_CHECK_FILE_HANDLE`, `SMB2SRV_CALL_NTVFS_BACKEND`, and async status variants.

## Control Flow
Command handlers use the macros as structured control flow: validate body and fixed-size tag, allocate request-local IO, build an NTVFS request attached to the tcon backend and session info, dispatch either synchronously or asynchronously, and convert errors into SMB2 error replies. Async send callbacks use the check macros to retrieve `req` and the typed IO object, terminate connections on close/write-fault states, and either propagate errors or continue serialization.

## State And Persistence
The header defines only in-memory state. The request object is central to per-packet state, chained request propagation, pending async identity, and reply signing. Persistence is delegated to session/tcon/NTVFS structures referenced from it.

## Dependencies And Integration Points
It depends on `smb_server.h`, generated prototypes, NTVFS async semantics, talloc, NTSTATUS helpers, and SMB2 buffer structs. Nearly every file in `source4/smb_server/smb2` depends on these definitions.

## Risks And Test Signals
Risks include macros that early-return and obscure cleanup, assumptions that `req->tcon` and `req->session` are valid before NTVFS setup, exact fixed-size tag arithmetic for dynamic bodies, and divergent behavior between `_ERR` and strict OK async checks. Tests should exercise every command’s malformed body path, async success/error/close paths, no-memory simulation, invalid handle translation, and compounded requests that carry chained session/tree/file state.
