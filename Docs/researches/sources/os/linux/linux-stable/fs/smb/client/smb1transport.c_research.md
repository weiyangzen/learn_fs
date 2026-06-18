# File Research: sources/os/linux/linux-stable/fs/smb/client/smb1transport.c

## Purpose
Implements SMB1/CIFS transport helpers for request setup, send/receive wrappers, response validation, signature verification, MID queue management, and multi-part TRANSACTION2 response coalescing.

## Main Responsibilities
- Allocate and initialize SMB1 MID queue entries.
- Enforce session state constraints before sending SMB1 requests.
- Sign SMB1 requests and verify signed responses.
- Provide legacy `SendReceive*()` wrappers around the shared CIFS transport path.
- Validate SMB1 response headers and lengths.
- Detect and merge multi-response TRANSACTION2 replies.

## Key Functions
- `alloc_mid()` creates a `mid_q_entry`, initializes refcount/lock, records MID, PID, command, allocation time, creator task, default callback, and state.
- `allocate_mid()` checks `SES_NEW`/`SES_EXITING` state rules, then adds the MID to `server->pending_mid_q`.
- `cifs_setup_async_request()` enables signing when needed, allocates a MID, and signs an async request.
- `cifs_setup_request()` is the synchronous setup path with session-aware MID allocation and request signing.
- `SendReceiveNoRsp()`, `SendReceive2()`, and `SendReceive()` adapt older CIFS call sites to `cifs_send_recv()`.
- `cifs_check_receive()` dumps the SMB, verifies signatures when signing is enabled, handles reconnect on optional signing failure, then maps SMB errors.
- `check2ndT2()` detects incomplete SMB1 TRANSACTION2 replies and returns missing byte count.
- `coalesce_t2()` appends secondary TRANSACTION2 data into the first response while updating `DataCount`, BCC, and PDU length.
- `cifs_check_trans2()` coordinates multi-response TRANSACTION2 state on the MID.
- `check_smb_hdr()` validates SMB1 protocol signature and permits only legitimate server-to-client exceptions.
- `checkSMB()` validates SMB1 frame length, word count/BCC reachability, protocol header, calculated size, RFC1001 length, and tolerated legacy over-padding.

## Important Data Flow
1. SMB1 callers build a request buffer and pass it through setup/send wrappers.
2. A MID is allocated and queued before the request is sent.
3. Signing state is applied before transmission.
4. Responses are checked for SMB framing consistency and, when needed, signature validity.
5. TRANSACTION2 responses may remain queued until all secondary fragments are coalesced.
6. Final status is converted to Linux/POSIX errors by the common SMB error mapping path.

## Edge Cases and Defensive Logic
- Rejects oversized outbound frames.
- Allows negotiate/session setup during `SES_NEW`, and logoff during `SES_EXITING`.
- Handles legacy servers that return short error packets or one-byte BCC quirks.
- Allows certain malformed-looking but historically observed TRANSACTION2 error responses.
- Caps tolerated trailing data to 512 bytes except for known BCC wrap cases.
- Prevents TRANSACTION2 coalescing overflows in `DataCount`, BCC, and response buffer length.

## Dependencies
Uses CIFS core structures and helpers from `cifsglob.h`, `cifsproto.h`, `smb1proto.h`, `smb2proto.h`, `cifs_debug.h`, `smbdirect.h`, and `compress.h`.
