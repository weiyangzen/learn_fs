# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb2_rq.c

## Purpose

`smb2_rq.c` implements SMB2/3 request header construction, enqueueing, waiting, reply verification, and SMB2 header parsing for the SMB client.

## Main Interfaces

Exported functions are `smb2_rq_fillhdr()`, `smb2_rq_simple()`, `smb2_rq_simple_timed()`, `smb2_rq_internal()`, and `smb2_rq_parsehdr()`. Internal helpers are `smb2_rq_enqueue()` and `smb2_rq_reply()`.

## Behavior And Data Flow

`smb2_rq_fillhdr()` rewinds a duplicate of the first request mblk and writes the 64-byte SMB2 header: protocol signature, structure size, credit charge/request, status placeholder, command, flags, next-command offset, message ID, process ID, tree ID, and session ID. The signature field is left for signing code.

`smb2_rq_simple_timed()` prepares a request state and timeout, enqueues it, then waits for and parses the reply. `smb2_rq_enqueue()` handles reconnect and tree-connect state unless `SMBR_NORECONNECT` is set, fills request session/tree IDs, and queues through `smb2_iod_addrq()`.

`smb2_rq_internal()` is for IOD connection setup and echo-like internal requests. It bypasses reconnect/tree-connect logic, marks requests internal, waits with `smb_iod_waitrq_int()`, verifies signed non-encrypted replies, parses headers, and deliberately leaves raw NT status for callers.

`smb2_rq_reply()` waits for normal replies, verifies signatures when the request was signed and the reply is not encrypted, parses the SMB2 header, maps NT status to errno, and treats `NT_STATUS_BUFFER_OVERFLOW` as non-fatal while marking `SMBR_MOREDATA`.

`smb2_rq_parsehdr()` decodes the SMB2 header, requires structure size 64, records status, command, credits, flags, next command, message ID, process/tree or async ID, session ID, and skips the 16-byte signature.

## Dependencies

This file depends on SMB request structures, IOD queue/wait helpers, reconnect and tree-connect helpers, SMB2 signing verification, mbchain/mdchain helpers, and NT-status-to-errno mapping.

## Research Notes

The key invariants are that headers are finalized only after message ID and tree/session IDs are known, signed replies are verified before header status is trusted, internal requests do not recursively reconnect, and buffer overflow status is exposed through flags rather than returned as a hard error.
