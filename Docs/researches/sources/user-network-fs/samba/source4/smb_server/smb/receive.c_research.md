# sources/user-network-fs/samba/source4/smb_server/smb/receive.c

## Purpose
Provides the SMB1 receive and dispatch path for a connection. It validates NBT/SMB framing, initializes `smbsrv_request`, computes request buffer metadata, checks SMB signing, enforces session/tree requirements, dispatches commands through the SMB command table, supports AndX chaining, emits oplock breaks, and initializes SMB1 connection defaults.

## Important APIs, Types, And Functions
- `smb_messages[256]` maps SMB command bytes to names, handler functions, and flags (`NEED_SESS`, `NEED_TCON`, `SIGNING_NO_REPLY`, `AND_X`, `LARGE_REQUEST`).
- `smbsrv_recv_smb_request()` is the packet callback for SMB1 requests.
- `switch_message()` resolves tcon/session, performs authorization preconditions, adjusts special signing no-reply sequence behavior, and calls the handler.
- `smbsrv_chain_reply()` advances a single request through an AndX chain by replacing `req->in.vwv`, `req->in.data`, and related metadata.
- `smbsrv_send_oplock_break()` builds an async `SMBlockingX` oplock break packet.
- `smbsrv_init_smb_connection()` initializes max transmit values, time zone offset, NT status support, session/tcon tables, and signing state.

## Control Flow
NBT session packets with nonzero type are diverted to `smbsrv_reply_special()`. Normal packets must contain the SMB magic and enough bytes for the header. The receive path creates a request, points it into the packet buffer, reads word count/data count, handles oversized large requests for flagged commands, validates word/data bounds, sets `flags2`, initializes `request_bufinfo`, then verifies incoming signing. Dispatch performs table lookup, resolves TID and UID to `req->tcon` and `req->session`, returns command-dependent errors for missing session/tcon, and runs the handler. Chaining validates the next command offset and word/data bounds, writes the previous response's AndX continuation fields, clears per-leg NTVFS/io state, and recursively dispatches the chained command.

## State And Persistence
Active async requests are linked in `smb_conn->requests` by the NTVFS macros, and the request destructor removes them. Chained requests reuse the same request object and carry `chain_count`, `chained_fnum`, current session, and output buffer. Connection initialization persists session and tree ID allocators plus signing settings. Oplock break packets are synthetic requests with MID/PID/UID values set to wildcard-style constants.

## Dependencies And Integration Points
Dispatches into handlers implemented by `reply.c`, `negprot.c`, `search.c`, `trans2.c`, and `nttrans.c`. Uses request helpers from `request.c`, signing helpers from `signing.c`, session/tcon lookup helpers, packet termination/send infrastructure, and NTVFS oplock callbacks configured by `service.c`.

## Risks
This is a primary wire-input boundary. Bounds checks on `wct`, data size, AndX offsets, and large request sizing are critical. Missing session/tcon errors intentionally vary by command and negotiated NT-status capability, so compatibility tests matter. `SIGNING_NO_REPLY` has special behavior for `SMBntcancel`; incorrect sequence adjustment can break signing. Chaining mutates request internals and frees per-leg NTVFS/io state, so handler assumptions about lifetime are important.

## Test Signals
Cover invalid NBT/SMB headers, truncated word/data sections, large WriteX and NTTrans sizing, unsupported commands, missing session/tcon error mapping, signed and unsigned requests, `SMBntcancel` no-reply signing sequence behavior, valid and invalid AndX chains, and SMB connection initialization under different loadparm settings.
