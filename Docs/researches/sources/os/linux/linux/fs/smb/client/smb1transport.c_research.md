# File Research: sources/os/linux/linux/fs/smb/client/smb1transport.c

This file implements SMB1/CIFS transport-side request setup, send/receive wrappers, response validation, signing verification, MID tracking, and multi-response Transaction2 coalescing.

Primary responsibilities:
- Allocate and initialize SMB1 `mid_q_entry` objects through `alloc_mid()` and `allocate_mid()`.
- Enforce session state rules before queuing requests: normal commands are rejected while sessions are new or exiting, except negotiate/session-setup/logoff cases.
- Prepare signed synchronous and asynchronous SMB requests with `cifs_setup_request()` and `cifs_setup_async_request()`.
- Provide legacy send helpers: `SendReceiveNoRsp()`, `SendReceive2()`, and `SendReceive()`.
- Validate received SMB1 frames with `checkSMB()`.
- Verify SMB signatures in `cifs_check_receive()` and map SMB errors to Linux errors.
- Detect and merge multi-part SMB_COM_TRANSACTION2 responses via `check2ndT2()`, `coalesce_t2()`, and `cifs_check_trans2()`.

Important control flow:
- `alloc_mid()` assigns MID, PID, command, allocation time, default wakeup callback, creator task reference, refcount, and initial `MID_REQUEST_ALLOCATED` state.
- `allocate_mid()` protects session-status checks with `ses_lock`, then inserts the MID into `server->pending_mid_q` under `mid_queue_lock`.
- `cifs_setup_async_request()` enables signature flags when required, signs the request, and returns an `ERR_PTR()` on failure.
- `SendReceive()` validates transmit length, session/server pointers, maximum CIFS buffer size, sends via `cifs_send_recv()`, copies the response into caller storage when requested, and frees the response buffer.
- `cifs_check_trans2()` stores the first large Transaction2 response, then coalesces later secondary responses until all data is present or a malformed response ends the MID.

Validation and safety:
- Transmit requests larger than the SMB1/RFC1001 frame limit or `CIFSMaxBufSize + MAX_CIFS_HDR_SIZE` are rejected.
- `check_smb_hdr()` verifies the SMB1 protocol signature and rejects unexpected server-to-client requests except oplock/locking and known malformed Transaction2 error replies.
- `checkSMB()` validates minimum header/BCC availability, `WordCount`, calculated SMB size, RFC1001 length, BCC wraparound for large reads, and limits tolerated trailing server padding to 512 bytes.
- `coalesce_t2()` checks total data counts, 16-bit field overflow, final PDU size bounds, and target buffer capacity before appending secondary response data.
- Signature mismatch triggers reconnect when signing was not mandatory; mandatory-signing failures remain hard errors.

Dependencies:
- CIFS MID pool, server pending queue, SMB1 header helpers, request signing/verification, `cifs_send_recv()`, response buffer lifetime helpers, error mapping, and trace/error helpers.

Research notes:
- This is the SMB1 transport guardrail layer. Most higher-level SMB1 operations depend on it to reject malformed frames early and keep request/MID lifecycle state coherent.
- Transaction2 coalescing is security-sensitive because it adjusts in-buffer lengths and copies server data into the first response buffer.
- Several compatibility branches intentionally tolerate historical server bugs, including missing BCC bytes, absent response flags on some errors, BCC wraparound, and limited extra trailing data.
