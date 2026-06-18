# sources/user-network-fs/samba/source4/smb_server/smb2/receive.c

## Purpose
This file is the SMB2 receive, dispatch, reply, chaining, async-pending, cancel, and connection-initialization core. It turns incoming NBT-framed SMB2 packets into `smb2srv_request` objects, validates framing, routes opcodes to command handlers, signs replies when required, and tracks asynchronous requests for cancellation.

## Important APIs, Types, And Functions
Key public functions are `smb2srv_setup_bufinfo`, `smb2srv_init_request`, `smb2srv_setup_reply`, `smb2srv_send_reply`, `smb2srv_send_error`, `smbsrv_recv_smb2_request`, `smb2srv_queue_pending`, `smb2srv_cancel_recv`, and `smbsrv_init_smb2_connection`. Important internal pieces are request destructors, `smb2srv_chain_reply`, `smb2srv_reply`, and `smb2srv_init_pending`.

## Control Flow
`smbsrv_recv_smb2_request` validates the NBT byte, minimum length, SMB2 magic, body size, dynamic area, and first-request related flag, then calls `smb2srv_reply`. The dispatcher checks header length, monotonic message IDs, related-request session/tcon inheritance, session/tcon lookup, signing verification/enforcement, prior chain failure state, and opcode requirements before calling command-specific receive functions. Replies are built by `smb2srv_setup_reply`, queued by `packet_send`, optionally signed, and followed by chained-request dispatch if `NextCommand` is set. Async backends call `smb2srv_queue_pending`, which allocates an async id, emits `NT_STATUS_PENDING`, and keeps the request protected until final completion. CANCEL looks up async ids and calls `ntvfs_cancel`.

## State And Persistence
The file owns transient request lifetime and mutates connection state: highest SMB2 sequence number, pending request id tree/list, request timestamps, and SMB2 connection defaults. Persistent file/session/share effects are elsewhere. Request destructors remove pending ids and linked-list entries.

## Dependencies And Integration Points
It depends on packet transport, idtree, signing helpers, session and tcon lookup, NTVFS cancellation, command handlers from sibling SMB2 files, and common server structures from `smb_server.h`. `smb_server.c` installs `smbsrv_recv_smb2_request` as the packet callback after protocol detection.

## Risks And Test Signals
Risks include strict sequence-number handling under replay or compounding, dynamic-size underflow, related-request propagation bugs, signing state mismatches, async destructor denial while pending, and always using `NT_STATUS_INVALID_PARAMETER` as chain failure after error replies. Tests should include malformed NBT/SMB2 headers, chained compounds with and without related flags, signed and unsigned session traffic, async pending plus cancel, out-of-order message ids, invalid session/tcon ids, and socket teardown during send.
