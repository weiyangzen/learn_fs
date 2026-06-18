# sources/user-network-fs/libsmb2/lib/smb2-cmd-read.c

## Purpose
Builds SMB2 READ requests and replies and parses READ replies/requests for client and server modes.

## Important APIs, Types, And Functions
The public command functions are `smb2_cmd_read_async` and `smb2_cmd_read_reply_async`. Receive handlers are `smb2_process_read_fixed`, `smb2_process_read_variable`, `smb2_process_read_request_fixed`, and `smb2_process_read_request_variable`. `free_read_reply` releases copied reply data when the application supplied a receive buffer.

## Control Flow
Request encoding writes flags, length, offset, file id, minimum count, channel, remaining bytes, and optional channel info. Without multi-credit support, reads above 64 KiB are capped and minimum count is cleared. A one-byte dummy buffer is appended when no channel info exists because SMB2 requires a buffer field. `smb2_cmd_read_async` adds caller-provided reply storage to `pdu->in` so the generic socket reader can place data directly. Reply encoding emits a fixed reply header and appends data when present. Reply parsing validates data offset and returns the variable data length for the socket state machine; variable parsing either copies into the application buffer or points `rep->data` at the receive iovec for zero copy.

## State And Persistence
Read length and output buffer ownership are tied to PDU lifetime. If the application provides `req->buf`, the payload is copied and `free_read_reply` frees it later; otherwise the reply data pointer is valid only as long as the PDU/input vector is retained. Request parsing stores file id, length, offset, and channel data pointers in the PDU payload.

## Dependencies And Integration Points
The code depends on credit accounting, max read size enforcement, iovec receive injection, PDU padding, and the generic fixed/variable parser. It integrates with server callbacks that consume parsed `struct smb2_read_request`.

## Risks
In `smb2_process_read_request_fixed`, `req->read_channel_info_length` is tested before it is loaded from the wire, so channel-info offset handling can be wrong. Data offset validation for replies expects exactly `SMB2_HEADER_SIZE + 16`, which is intentionally strict. Channel info is only encoded outside passthrough by returning an unsupported error. Server request parsing enforces max read size but does not deeply validate channel data semantics.

## Test Signals
Test reads with zero and nonzero lengths, caller-supplied and zero-copy buffers, >64 KiB requests with and without multi-credit, malformed data offsets, read requests above `max_read_size`, passthrough channel info, and channel-info length/offset fuzzing.
