# sources/user-network-fs/samba/source4/smb_server/smb2/fileio.c

## Purpose
This file implements the SMB2 file-oriented command adapters for the source4 SMB server. It parses SMB2 CREATE, CLOSE, FLUSH, READ, WRITE, LOCK, IOCTL, NOTIFY, and BREAK request bodies into Samba raw/NTVFS request unions, validates handles and dynamic buffers, calls the NTVFS backend, and serializes SMB2 replies.

## Important APIs, Types, And Functions
The public entry points are `smb2srv_create_recv`, `smb2srv_close_recv`, `smb2srv_flush_recv`, `smb2srv_read_recv`, `smb2srv_write_recv`, `smb2srv_lock_recv`, `smb2srv_ioctl_recv`, `smb2srv_notify_recv`, and `smb2srv_break_recv`. Each has a matching static send callback, such as `smb2srv_create_send` or `smb2srv_read_send`, reached through `SMB2SRV_SETUP_NTVFS_REQUEST`. The code relies on `union smb_open`, `union smb_close`, `union smb_read`, `union smb_write`, `union smb_lock`, `union smb_ioctl`, and `union smb_notify`, plus SMB2 blob helpers and NTVFS operations.

## Control Flow
Receive functions first enforce the SMB2 fixed structure size with `SMB2SRV_CHECK_BODY_SIZE`, allocate an IO union under the request, decode little-endian fields and offset/length dynamic areas, resolve file handles with `smb2srv_pull_handle`, and dispatch via `SMB2SRV_CALL_NTVFS_BACKEND`. Send callbacks check async completion, build replies with `smb2srv_setup_reply`, write fixed fields, append dynamic data where needed, and call `smb2srv_send_reply`. CREATE additionally parses create-context blobs for EAs, security descriptors, durable-handle fields, allocation size, maximal access, timewarp, and query-on-disk-id, and emits MXAC/QFID reply blobs.

## State And Persistence
The file does not persist data itself. It mutates per-request state, especially `req->io_ptr`, `req->ntvfs`, `req->chained_file_handle`, and sometimes `req->tcon` through handle resolution. Persistent effects are delegated to NTVFS backends: file creation, writes, locks, flushes, notification registrations, ioctl work, and oplock break acknowledgement.

## Dependencies And Integration Points
It depends on `libcli/smb2` framing helpers, raw SMB unions, NDR security descriptor decoding, EA parsing, `ntvfs_*` calls, and the common SMB2 request macros in `smb2_server.h`. It is invoked from `receive.c` dispatch after session and tree-connect validation. Handle format and chained-handle behavior integrate with `smb2/tcon.c`.

## Risks And Test Signals
Important risks are exact SMB2 structure-size compliance, offset/length validation in dynamic blobs, memory pressure when preallocating read buffers, CREATE context length checks, NULL-name fallback behavior, lock-count overflow, wildcard or stale handle handling, and TODO-marked extra copies. Test signals include SMB2 create contexts, reads with one-byte dynamic tail, writes with dynamic payloads, multi-lock requests, no-handle IOCTLs, notifications with Unicode names and alignment, oplock breaks, chained requests reusing a CREATE handle, and malformed length/handle cases.
